#  here all data extraction/scrapping methods and data normalization defined

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import URLs
import re
import numpy as np


def get_quarterly_values(ticker, parameter, outliers='qqq', quarters=20):
    url = URLs.url_general.format(ticker=ticker) + URLs.sub_urls[parameter]
    table_list = pd.read_html(url)
    for t in table_list:
        if 'Quarterly' in ''.join(t.columns.values) and parameter in ''.join(t.columns.values):
            table = t
            break
    if not table.empty:
        n = 10**6 if '(Millions of US $)' in ''.join(table.columns.values) else 10**0
        table.columns = ('date', parameter)
        table['date'] = table['date'].astype('datetime64')
        table = table.set_index(table.columns.values[0])
        table[parameter] = table[parameter].str.replace(',', '')
        table[parameter] = table[parameter].str.replace('$', '')
        if outliers == 'drop' and table.isna().values.any():
            print('NaN values found in {} {} and dropped'.format(ticker, parameter))
            table = table.dropna()
        table[parameter] = table[parameter].astype('float')
        table[parameter] = table[parameter] * n
        table = table.head(quarters).iloc[::-1]
        table, growth_rate = add_linear_regression(table)
        return table, growth_rate
    else:
        print('no data found for {} {}'.format(ticker, parameter))


def get_market_cap(ticker):
    url = URLs.url_general.format(ticker=ticker) + URLs.sub_urls['Market Cap']
    soup = bs(requests.get(url).content, 'html.parser')
    match = re.search('[0-9a-zA-Z ]+ market cap as of [0-9a-zA-Z ]+, [0-9]{4} is .(\\d+.\\d+B).', soup.text)
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


def add_linear_regression(arr):  # get 1D pandas DF (array) and add linear forecast column
    #arr = arr.fillna(0)
    t1 = np.arange(arr.size)
    t2 = np.arange(arr.size + 12)
    line = np.polyfit(t1, arr.values, 1)
    index2 = arr.index.union(pd.date_range(arr.index[-1], periods=13, freq='3M')[1:])
    arr2 = pd.DataFrame(data=line[0] * t2 + line[1] * np.ones(len(t2)), index=index2, columns=('lin reg',))
    arr_res = pd.concat((arr, arr2), axis=1)
    return arr_res, line[0]
