import logging; logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)

import pandas as pd
import numpy.testing as npt

from capon.backends import nasdaq


def test_existing_symbol():
    metadata = nasdaq.metadata('AMZN')

    assert type(metadata) == pd.Series
    assert metadata['symbol']=='AMZN'


# def test_invalid_symbol():
#     metadata = nasdaq.metadata(':):)')
#
#     assert type(metadata) == pd.Series
#     assert len(metadata) == 0


if False:
    df = pd.concat([nasdaq.metadata(s) for s in ['AMZN', 'GOOGL', 'AAAU']], axis=1).T
    df['symbol']
