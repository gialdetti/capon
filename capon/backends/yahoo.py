"""Backend implementation for Yahoo Finance.

"""

import logging
import os
import requests

import pandas as pd


ROOT = os.path.dirname(__file__)
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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    }
    response = requests.get(url, headers=headers)
    logging.info(f'{response.url}.. {response.status_code}')

    jo = response.json()

    if response.status_code!=200:
        print(f'STATUS {response.status_code}:', jo['chart']['error']['description'])

    return jo


def stock(symbol, range='1d', interval=None):
    """Get historical stock prices.

    Parameters
    ----------
    symbol : str
        The ticker symbol of the required stock.
    range : {'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'}, default '1d'
        Specify the timeframe for the required data.
    interval : {None, '1m', '2m', '15m', '1h', '1d', '1wk', '1mo'}, default None
        Specify the time interval for the required data.
        If None, then the default interval of the specified `range` is used.

    Returns
    -------
    DataFrame
        Listing stock price features for all timepoints in the required timeframe. Each row includes the open, high,
        low, and close price for a given timepoint. If relevant, it will also include the adjusted closing price.
    """
    jo = get_stock(symbol, range=range, interval=interval)

    result = jo['chart']['result'][0]
    metadata = result['meta']
    ts = pd.DataFrame({
        'timestamp': pd.to_datetime(result.get('timestamp', []), unit='s').tz_localize('UTC').tz_convert(metadata['gmtoffset']),
        'symbol': metadata['symbol'],
        'currency': metadata['currency'],
    })
    quote = pd.DataFrame(result['indicators']['quote'][0])
    adjclose = pd.DataFrame(result['indicators']['adjclose'][0]) if 'adjclose' in result['indicators'] else None

    # len(ts), len(quote), len(adjclose)
    stock = pd.concat([ts, quote, adjclose], axis=1)        
    return stock


