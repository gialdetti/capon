import logging
import re
import requests


def get_json(url, headers={}):
    response = requests.get(url, headers=headers)
    logging.info(f'{response.url}.. {response.status_code}')

    jo = {}
    if response.status_code==200:
        jo = response.json()

    return jo


def camel_case_keys(df):
    last_dim = len(df.shape)-1
    df = df.rename({k: camel_to_snake_case(k) for k in df.keys()}, axis=last_dim) \
        .rename({
            'forward_pe1_yr': 'forward_pe_1_yr',
            'is_nasdaq100': 'is_nasdaq_100',
        }, axis=last_dim)
    return df


def camel_to_snake_case(name):
    name = re.sub(' ', '', name)
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    return name


if False:
    camel_to_snake_case('getHTTPResponseCode') == 'get_http_response_code'
    camel_to_snake_case('ForwardPE1Yr') == 'forward_pe1_yr'
    camel_to_snake_case('Security Name') == 'security_name'
