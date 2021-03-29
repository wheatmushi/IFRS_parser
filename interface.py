#  here all data extraction/scrapping methods and data normalization defined

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import URLs
import re
import numpy as np


def get_quarterly_values(ticker, parameter, outliers=False, linear_source=(-20, 0), forecast=12):
    url = URLs.url_general.format(ticker=ticker) + URLs.sub_urls[parameter]
    table_list = pd.read_html(url)
    for t in table_list:
        if 'Quarterly' in ''.join(t.columns.values) and parameter in ''.join(t.columns.values):
            table = t
            break
    if table.empty:
        print('no data found for {} {}'.format(ticker, parameter))
        return

    n = 10**6 if '(Millions of US $)' in ''.join(table.columns.values) else 10**0
    table.columns = ('date', parameter)
    table['date'] = table['date'].astype('datetime64')
    table = table.set_index(table.columns.values[0])
    table[parameter] = table[parameter].str.replace(',', '')
    table[parameter] = table[parameter].str.replace('$', '')
    table[parameter] = table[parameter].astype('float')
    table[parameter] = table[parameter] * n
    table = table.iloc[::-1]
    table, growth_rate = add_linear_regression(table, outliers=outliers, linear_source=linear_source, forecast=forecast)
    return table, growth_rate


def get_market_cap(ticker):
    url = URLs.url_general.format(ticker=ticker) + URLs.sub_urls['Market Cap']
    soup = bs(requests.get(url).content, 'html.parser')
    match = re.search('[0-9a-zA-Z ]+ market cap as of [0-9a-zA-Z ]+, [0-9]{4} is .(\\d+.\\d+)B.', soup.text)
    cap = match.group(1)
    if not cap or cap == 0:
        print('{} market cap undefined'.format(ticker))
    return float(cap) * 10**9


def get_price(ticker):
    url = URLs.url_general.format(ticker=ticker) + URLs.sub_urls['Price']
    soup = bs(requests.get(url).content, 'html.parser')
    match = re.search('The latest closing stock price for [0-9a-zA-Z ]+ as of [0-9a-zA-Z ]+, [0-9]{4} is (\\d+.\\d+).',
                      soup.text)
    price = match.group(1)
    if not price or price == 0:
        print('{} price undefined'.format(ticker))
    return float(price)


def add_linear_regression(arr, outliers, linear_source, forecast):
    # get 1D pandas DF (array) and add linear forecast column with optional removal of outliers
    old_data = arr.iloc[0: arr.shape[0]+linear_source[0]]  # data excluded from linearization
    source = arr.iloc[arr.shape[0]+linear_source[0]: arr.shape[0]+linear_source[1]]  # source for linear regression
    new_data = arr.iloc[arr.shape[0]+linear_source[1]:]  # in case if linearization counted not on latest data

    t1 = np.arange(old_data.shape[0])
    t2 = np.arange(old_data.shape[0], old_data.shape[0] + source.shape[0])  # X-axis for linear regression
    t3 = np.arange(old_data.shape[0] + source.shape[0], old_data.shape[0] + source.shape[0] + new_data.shape[0])
    t4 = np.arange(old_data.shape[0] + source.shape[0] + new_data.shape[0],
                   old_data.shape[0] + source.shape[0] + new_data.shape[0] + forecast)

    line = np.polyfit(t2, source.values, 1)
    last_index = new_data.index[-1] if not new_data.empty else source.index[-1]
    last_index = last_index + pd.Timedelta(90, 'D')
    forecasted_data = pd.DataFrame(data=t4, columns=['t'], index=pd.date_range(last_index, periods=forecast, freq='3M'))
    old_data['t'], source['t'], new_data['t'] = t1, t2, t3

    arr_res = pd.concat((old_data, source, new_data, forecasted_data), axis=0)
    arr_res['linear_regression'] = line[0] * arr_res['t'] + line[1]
    return arr_res, line[0]
