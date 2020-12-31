import logging; logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)

import pandas as pd
import numpy.testing as npt

from capon.backends import nasdaq


def test_existing_symbol():
    symbol = 'AMZN'
    metadata = nasdaq.metadata(symbol)

    assert type(metadata) == pd.Series
    assert metadata.name == symbol
    assert metadata['symbol'] == symbol


def test_invalid_symbol():
    bad_symbol = ':):)'
    metadata = nasdaq.metadata(bad_symbol)

    assert type(metadata) == pd.Series
    assert metadata.name == bad_symbol
    assert len(metadata) == 0


if False:
    df = pd.concat([nasdaq.metadata(s) for s in ['AMZN', 'GOOGL', 'AAAU']], axis=1).T
    df['symbol']
