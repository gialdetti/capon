import logging
import re

import requests
import pandas as pd


def metadata(symbol):
    url = f'https://api.nasdaq.com/api/company/{symbol}/company-profile'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
    }
    jo = get_json(url, headers)

    if ('data' in jo) and (jo['data'] is not None):
        metadata = pd.DataFrame(jo['data']).loc['value'].rename(symbol)
        metadata = metadata.rename({k: camel_to_snake_case(k) for k in metadata.keys()})
    else:
        metadata = pd.Series([], name=symbol)

    return metadata


def get_json(url, headers={}):
    response = requests.get(url, headers=headers)
    logging.info(f'{response.url}.. {response.status_code}')

    jo = {}
    if response.status_code==200:
        jo = response.json()

    return jo


def camel_to_snake_case(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
