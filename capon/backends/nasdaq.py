import pandas as pd

from capon.backends.utils import get_json, camel_case_keys

urls = {
    'screener': 'https://api.nasdaq.com/api/screener/stocks?tableonly=true&exchange={exchange}&download=true',

    'profile':'https://api.nasdaq.com/api/company/{symbol}/company-profile',
    'info':'https://api.nasdaq.com/api/quote/{symbol}/info?assetclass=stocks',
    'summary':'https://api.nasdaq.com/api/quote/{symbol}/summary?assetclass=stocks',
    'chart':'https://api.nasdaq.com/api/quote/{symbol}/chart?assetclass=stocks&fromdate={from_date}&todate={to_date}'
}

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}


def screener(exchange=''):
    """Full stock metadata allowing further screening.

    Parameters
    ----------
    exchange : {'', 'NASDAQ', 'NYSE', 'AMEX'}, default ''
        The stock exchange of the required list. By default will return symbols from all stock exchanges.


    Returns
    -------
    DataFrame
        Listing of all stocks and their basic metadata (e.g., market_cap, industry, sector).
    """

    url = urls['screener'].format(exchange=exchange)
    jo = get_json(url, headers)
    metadata = pd.DataFrame(jo['data']['rows']).pipe(camel_case_keys)

    return metadata


def metadata(*args, **kwargs):
    return profile(*args, **kwargs)


def profile(symbol):
    url = urls['profile'].format(symbol=symbol)
    jo = get_json(url, headers)

    if ('data' in jo) and (jo['data'] is not None):
        profile = pd.DataFrame(jo['data']).loc['value'].rename(symbol) \
            .pipe(camel_case_keys)
    else:
        profile = pd.Series(None, name=symbol)

    return profile


def info(symbol):
    url = urls['info'].format(symbol=symbol)
    jo = get_json(url, headers)
    info = pd.Series(jo['data'], name=symbol).pipe(camel_case_keys)

    return info


def summary(symbol):
    url = urls['summary'].format(symbol=symbol)
    jo = get_json(url, headers)

    if (jo['data'] is not None):
        summary = pd.DataFrame(jo['data']['summaryData']).loc['value'].rename(symbol) \
            .pipe(camel_case_keys)
    else:
        summary = pd.Series(None, name=symbol)

    return summary


def chart(symbol, from_date='', to_date=''):
    url = urls['chart'].format(symbol=symbol, from_date=from_date, to_date=to_date)
    jo = get_json(url, headers)

    chart_metadata = pd.Series(jo['data'], name=symbol).pipe(camel_case_keys)
    if ((jo['data'] is not None) and (jo['data']['chart'] is not None)):
        chart_data = pd.DataFrame(chart_metadata['chart'])['z'].apply(pd.Series) \
            .assign(timestamp=lambda df: pd.to_datetime(df['dateTime'], dayfirst=True)).drop('dateTime', axis=1)
    else:
        chart_data = None

    return chart_data, chart_metadata






if False:
    symbol = 'AMZN'
    symbol = 'QUBT'

    profile(symbol)
    info(symbol)
    summary(symbol)
    chart(symbol)

    chart_data, chart_metadata = chart(symbol, from_date='2019-12-24', to_date='2020-12-31')


    metadata = screener()
    metadata.shape
    metadata.columns

