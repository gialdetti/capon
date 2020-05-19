import logging
import os
import requests
import json

import pandas as pd

# ROOT = "tests/test_stocke"
ROOT = os.path.dirname(__file__)

# Yahoo Finance


valid_range_intervals = {
    '1d': '2m', '5d': '15m', 
    '1mo': '1h', '3mo': '1d', '6mo': '1d', 
    '1y': '1wk', '2y': '1wk', '5y': '1mo', '10y': '1mo', 
    'ytd': '1d', 
    'max': '1m',
}


# # 1Y (w)
# url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval=1wk&range=1y&corsDomain=finance.yahoo.com&.tsrc=finance'
# # 1Y (d)
# url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval=1d&range=1y&corsDomain=finance.yahoo.com&.tsrc=finance'
# # 1d
# url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval=2m&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance'


def get_stock(symbol, range='1d', interval=None):
    if range not in valid_range_intervals.keys():
        raise ValueError(f'range must be from {list(valid_range_intervals.keys())}, got \'{range}\'')
    interval = interval or valid_range_intervals[range]
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval={interval}&range={range}&corsDomain=finance.yahoo.com&.tsrc=finance'

    headers = {}
    response = requests.get(url, headers=headers)
    logging.info(f'{response.url}.. {response.status_code}')

    jo = response.json()

    if response.status_code!=200:
        print(f'STATUS {response.status_code}:', jo['chart']['error']['description'])

    return jo


# jo = get_stock('AMZN')
# jo = get_stock('ALLY')
# print(jo.keys(), 
#     jo['chart'].keys(), 
#     len(jo['chart']['result']), 
#     jo['chart']['result'][0].keys(), 
#     jo['chart']['result'][0]['indicators'].keys(), 
#     len(jo['chart']['result'][0]['indicators']['quote'])
# )


# def stock(symbol, range='1d', interval=None):
#     jo = get_stock(symbol, range=range, interval=interval)

#     result = jo['chart']['result'][0]
#     metadata = result['meta']
#     ts = pd.DataFrame({
#         'timestamp': pd.to_datetime(result['timestamp'], unit='s') + pd.Timedelta(metadata['gmtoffset'], unit='s'),
#         'symbol': metadata['symbol']
#     })
#     quote = pd.DataFrame(result['indicators']['quote'][0])
#     adjclose = pd.DataFrame(result['indicators']['adjclose'][0]) if 'adjclose' in result['indicators'] else None

#     # len(ts), len(quote), len(adjclose)
#     stock = pd.concat([ts, quote, adjclose], axis=1)        
#     return stock



def stock(symbol, range='1d', interval=None):
    jo = get_stock(symbol, range=range, interval=interval)

    result = jo['chart']['result'][0]
    metadata = result['meta']
    ts = pd.DataFrame({
        'timestamp': pd.to_datetime(result.get('timestamp', []), unit='s') + pd.Timedelta(metadata['gmtoffset'], unit='s'),
        'symbol': metadata['symbol'],
        'currency': metadata['currency'],
    })
    quote = pd.DataFrame(result['indicators']['quote'][0])
    adjclose = pd.DataFrame(result['indicators']['adjclose'][0]) if 'adjclose' in result['indicators'] else None

    # len(ts), len(quote), len(adjclose)
    stock = pd.concat([ts, quote, adjclose], axis=1)        
    return stock


# jo = get_stock('MPNGY')
# stock('MPNGY')

if False:
    s = stock('AMZN')
    display(s)

    # stock.plot(x='timestamp', y='close')

    import plotly.express as px; px.defaults.template = 'plotly_dark'
    px.line(s, x='timestamp', y='close', color='symbol')


if False:
    stock_ids = ['GOOGL', 'AMZN']
    stock_ids = ['ALLY', 'DFS']
    stocks = pd.concat([stock(stock_id) for stock_id in stock_ids])
    px.line(stocks, x='timestamp', y='close', color='symbol')


    a, b = stocks['symbol'].unique()
    a, b = stocks[stocks['symbol']==a], stocks[stocks['symbol']==b]
    a, b = a['close'].fillna(0), b['close'].fillna(0)

    import numpy as np
    import matplotlib.pyplot as plt
    c = np.correlate(a, b, 'full')
    plt.plot(c)

    plt.xcorr(a, b, usevlines=True, maxlags=50, normed=True, lw=2)


    df = stocks.pivot_table(index='timestamp', columns='symbol', values='close')
    df.plot(secondary_y='DFS')



def nasdaq(symbol):
    url = f'https://api.nasdaq.com/api/company/{symbol}/company-profile'

    headers = {}
    response = requests.get(url, headers=headers)
    logging.info(f'{response.url}.. {response.status_code}')
    jo = response.json()

    metadata = pd.DataFrame(jo['data']).loc['value'].rename(symbol)

    return metadata

if False:
    pd.concat([nasdaq(s) for s in ['AMZN', 'GOOGL']], axis=1).T

