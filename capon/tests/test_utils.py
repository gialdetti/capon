import numpy as np
import pandas as pd
import numpy.testing as npt
import pandas.testing as pdt

from capon.utils import listify, normalize_values


def test_listify():
    # Test integers
    assert listify(1) == [1]
    assert listify([1]) == [1]
    assert listify([1, 2]) == [1, 2]

    # Test strings
    assert listify('aa') == ['aa']
    assert listify(['aa']) == ['aa']
    assert listify(['aa', 'bb']) == ['aa', 'bb']

    # Test numpy arrays
    npt.assert_array_equal(listify(np.array([1, 2])), np.array([1, 2]))

    # Test timestamp
    ts = pd.Timestamp(10)
    assert listify(ts) == [ts]
    assert listify([ts]) == [ts]
    assert listify([ts, ts]) == [ts, ts]


def test_normalize_values():
    stocks = pd.DataFrame([
        [1, 'A', 10, 150],
        [2, 'A', 20, 200],
        [3, 'A', 30, 250],
        [1, 'B', 0, 400],
        [2, 'B', 20, 800],
        [3, 'B', 40, 1200],

    ], columns=['timestamp', 'symbol', 'adjclose', 'open'])
    stocks['timestamp'] = pd.to_datetime(stocks['timestamp'].apply(lambda d: f'2020-01-{d:02} 10:00:00'))
    print(stocks)

    expected = pd.DataFrame([
        ['2020-01-01', 'A', -0.5, -0.25],
        ['2020-01-02', 'A',  0.0,  0.00],
        ['2020-01-03', 'A',  0.5,  0.25],
        ['2020-01-01', 'B', -1.0, -0.50],
        ['2020-01-02', 'B',  0.0,  0.00],
        ['2020-01-03', 'B',  1.0,  0.50],
    ], columns=['date', 'symbol', 'adjclose', 'open']).assign(date=lambda df: pd.to_datetime(df['date']))

    # single column
    stocks_normalized = normalize_values(stocks, '2020-01-02', values='adjclose').sort_values('symbol')
    # print(stocks_normalized)
    pdt.assert_frame_equal(stocks_normalized.reset_index(drop=True), expected[['date', 'symbol', 'adjclose']])

    # multiple columns
    stocks_normalized = normalize_values(stocks, '2020-01-02', values=['adjclose', 'open']).sort_values('symbol')
    # print(stocks_normalized)
    pdt.assert_frame_equal(stocks_normalized.reset_index(drop=True), expected)