import pandas as pd

from capon.backends.utils import camel_case_keys

urls = {
    'screener': 'https://www.otcmarkets.com/research/stock-screener/api/downloadCSV',
}


def screener():
    url = urls['screener']
    metadata = pd.read_csv(url).pipe(camel_case_keys)

    return metadata


if False:
    metadata = screener()
    metadata.columns