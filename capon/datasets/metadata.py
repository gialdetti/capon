import logging
import glob
import re

import pandas as pd

from .common import get_resource_path


stock_indexes = pd.DataFrame([
    ['^GSPC',     'S&P 500',      'S&P 500 Index (SPX)', 'US', 'New York'],
    ['^DJI',      'Dow 30',       'Dow Jones Industrial Average (DJIA)', 'US', 'New York'],
    ['^IXIC',     'Nasdaq',       'NASDAQ Composite Index (COMP)', 'US', 'New York'],
    ['^RUT',      'Russell 2000', 'Russell 2000 Index (RUT)', 'US', 'New York'],
    ['^GDAXI',    'DAX',          'DAX Pefromance Index (DAX)', 'Germany', 'Frankfurt'],
    ['^FTSE',     'FTSE 100',     'The Financial Times Stock Exchange 100 Index (UKX)', 'UK', 'London'],
    ['^N225',     'Nikkei 225',   'NIKKEI 225 Index (NIK)', 'Japan', 'Tokyo'],
    ['^TA125.TA', 'TA-125',       'Tel Aviv 125 Index (TA100)', 'Israel', 'Tel Aviv'],
    ['^BVSP',     'IBOVESPA',     '', 'Brazil', 'Sao Paolo'],
], columns=['symbol', 'name', 'description', 'country_code', 'city'])


def load_stock_indexes():
    """Major worldwide stock indexes

    Returns
    -------
    DataFrame
        Symbols and description for several worldwide stock indexes.

    References
    -------
    See https://finance.yahoo.com/world-indices/, or descriptions in https://www.marketwatch.com/investing/index/djia.

    """
    return stock_indexes.copy()


def load_metadata():
    metadata_filename = sorted(glob.glob(get_resource_path('metadata/stocks.metadata.*.gz')),
                               key=lambda s: parse_metadata_filename(s)['timestamp'])[-1]
    logging.info(f'Loading metadata from "{metadata_filename}"..')

    return pd.read_csv(metadata_filename)


def parse_metadata_filename(filename):
    m = re.match(r'.*stocks.metadata.x(?P<size>\d+)\.\((?P<timestamp>[0-9\.]+)\)\.csv.gz', filename)
    return m.groupdict()


