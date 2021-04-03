"""
Functions for fetching data from Macrotrends.
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import numpy as np

# Base Macrotrends URL with ticker and metric parameters
base_url = 'https://www.macrotrends.net/stocks/charts/{ticker}/xxx/{metric}'

# Company metrics with human-readable descriptions,
# taken from the corresponding Macrotrends pages
metric_descriptions = {
    # INCOME STATEMENT
    'revenue': 'Revenue',
    'gross-profit': 'Gross Profit',  # revenue with costs of sales excluded
    'research-development-expenses': 'Research and Development Expenses',
    'selling-general-administrative-expenses': 'SG&A Expenses',
    'ebitda': 'EBITDA',
    'operating-income': 'Operating Income',  # income before taxes and interest paid
    'net-income': 'Net Income',
    'eps-earnings-per-share-diluted': 'EPS',
    'shares-outstanding': 'Shares Outstanding',
    # PRICE
    'stock-price-history': 'Price',
    'market-cap': 'Market Cap',
    # BALANCE
    'total-liabilities': 'Total Liabilities',
    'total-assets': 'Total Assets'
}

def get_combined_quarterly_data(ticker, metrics):
    """ Produce a combined tabled of company metrics.

    ticker - a company ticker
    metrics - a list of company metrics
    """
    metrics_data = [get_quarterly_data_for_single_metric(ticker, metric) for metric in metrics]
    if metrics_data:
        return pd.concat(metrics_data, axis=1)
    else:
        return pd.DataFrame()
    
def get_quarterly_data_for_single_metric(ticker, metric):
    url = base_url.format(ticker=ticker, metric=metric)
    table_list = pd.read_html(url)
    table = pd.DataFrame()

    # Find a table on the webpage where headers contain
    # both the word "Quarterly" and a metric's description
    for t in table_list:
        column_headers = ''.join(t.columns.values)
        if 'Quarterly' in column_headers and metric_descriptions[metric] in column_headers:
            table = t
            break

    if table.empty:
        print('no data found for {} {}'.format(ticker, metric))
        return

    n = 10**6 if '(Millions of US $)' in ''.join(table.columns.values) else 10**0
    table.columns = ('date', metric)
    table['date'] = table['date'].astype('datetime64')
    table = table.set_index(table.columns.values[0])
    table[metric] = table[metric].str.replace(',', '', regex=False)
    table[metric] = table[metric].str.replace('$', '', regex=False)
    table[metric] = table[metric].astype('float')
    table[metric] = table[metric] * n
    table = table.iloc[::-1]
    return table


def get_market_cap(ticker):
    url = base_url.format(ticker=ticker, metric='market-cap')
    soup = bs(requests.get(url).content, 'html.parser')
    match = re.search('[0-9a-zA-Z ]+ market cap as of [0-9a-zA-Z ]+, [0-9]{4} is .(\\d+.\\d+)B.', soup.text)
    cap = match.group(1)
    if not cap or cap == 0:
        print('{} market cap undefined'.format(ticker))
    return float(cap) * 10**9


def get_price(ticker):
    url = base_url.format(ticker=ticker, metric='stock-price-history')
    soup = bs(requests.get(url).content, 'html.parser')
    match = re.search('The latest closing stock price for [0-9a-zA-Z ]+ as of [0-9a-zA-Z ]+, [0-9]{4} is (\\d+.\\d+).',
                      soup.text)
    price = match.group(1)
    if not price or price == 0:
        print('{} price undefined'.format(ticker))
    return float(price)