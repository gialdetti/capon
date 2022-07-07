import numpy as np
import pandas as pd

import numpy.testing as npt

from capon.preprocessing import shift


def create_dummy_stocks(n_symbols=2):
    stocks = pd.concat(
        [
            pd.DataFrame(
                {
                    "timestamp": pd.date_range("2020-01-01", "2022-01-01"),
                }
            ).assign(
                day=lambda df: df["timestamp"].dt.day_name(),
                symbol=chr(65 + i),
                close=lambda df: (i + 1) * 10000
                + df["timestamp"].dt.strftime("%Y.%m%d").astype(float),
            )
            for i in range(n_symbols)
        ],
        ignore_index=True,
    ).pipe(lambda df: df[df["timestamp"].dt.weekday <= 4])

    return stocks


def test_shift():
    df = pd.DataFrame(
        [
            ["2020-01-01", 1],
            ["2020-01-02", 2],
            ["2020-01-03", 3],
            #
            ["2020-01-05", 5],
            ["2020-01-06", 6],
            ["2020-01-07", 7],
        ],
        columns=["timestamp", "close"],
    ).assign(timestamp=lambda df: pd.to_datetime(df["timestamp"]))

    shifted = shift(df, days=(1, 2, 3))
    npt.assert_array_equal(shifted["close_next1days"], [2, 3, np.nan, 6, 7, np.nan])
    npt.assert_array_equal(
        shifted["close_next2days"], [3, np.nan, 5, 7, np.nan, np.nan]
    )
    npt.assert_array_equal(
        shifted["close_next3days"], [np.nan, 5, 6, np.nan, np.nan, np.nan]
    )

    filled = shift(df, days=(1, 2, 3), fillna="bfill")
    npt.assert_array_equal(filled["close_next1days"], [2, 3, 5, 6, 7, np.nan])
    npt.assert_array_equal(filled["close_next2days"], [3, 5, 5, 7, np.nan, np.nan])
    npt.assert_array_equal(filled["close_next3days"], [5, 5, 6, np.nan, np.nan, np.nan])


def test_shift_days_delta():
    stocks = create_dummy_stocks()
    g = stocks[stocks["symbol"] == "A"]

    # Past
    days = (-1, -7)
    windows = shift(g, days=days, fillna="ffill")
    assert len(windows) == len(g)
    assert all(g.columns.isin(windows.columns))

    # display(
    #     windows.iloc[0:].head(14).style.background_gradient(cmap="RdYlGn", axis=None)
    # )

    days_delta = windows[["timestamp"]].values - windows.filter(like="timestamp_prev")
    assert all(days_delta.min().dt.days >= np.abs(days))

    # Future
    days = (+1, +7)
    windows = shift(g, days=days, fillna="bfill")
    assert len(windows) == len(g)
    assert all(g.columns.isin(windows.columns))

    # display(
    #     windows.iloc[0:].tail(14).style.background_gradient(cmap="RdYlGn", axis=None)
    # )

    days_delta = windows.filter(like="timestamp_next") - windows[["timestamp"]].values
    assert all(days_delta.min().dt.days >= days)

    # windows = stocks.groupby('symbol').apply(shift)
