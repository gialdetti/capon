import numpy as np
import pandas as pd
import numpy.testing as npt
import pandas.testing as pdt

from capon.preprocessing import listify, normalize_traces


def test_listify():
    # Test integers
    assert listify(1) == [1]
    assert listify([1]) == [1]
    assert listify([1, 2]) == [1, 2]

    # Test strings
    assert listify("aa") == ["aa"]
    assert listify(["aa"]) == ["aa"]
    assert listify(["aa", "bb"]) == ["aa", "bb"]

    # Test numpy arrays
    npt.assert_array_equal(listify(np.array([1, 2])), np.array([1, 2]))

    # Test timestamp
    ts = pd.Timestamp(10)
    assert listify(ts) == [ts]
    assert listify([ts]) == [ts]
    assert listify([ts, ts]) == [ts, ts]


def test_normalize_traces():
    stocks = pd.DataFrame(
        [
            [1, "A", 10, 150],
            [2, "A", 20, 200],
            [3, "A", 30, 250],
            [1, "B", 0, 400],
            [2, "B", 20, 800],
            [3, "B", 40, 1200],
        ],
        columns=["timestamp", "symbol", "adjclose", "open"],
    )
    stocks["timestamp"] = pd.to_datetime(
        stocks["timestamp"].apply(lambda d: f"2020-01-{d:02} 10:00:00")
    )
    # print(stocks)

    expected = pd.DataFrame(
        [
            ["2020-01-01 10:00:00", "A", -0.5, -0.25],
            ["2020-01-02 10:00:00", "A", 0.0, 0.00],
            ["2020-01-03 10:00:00", "A", 0.5, 0.25],
            ["2020-01-01 10:00:00", "B", -1.0, -0.50],
            ["2020-01-02 10:00:00", "B", 0.0, 0.00],
            ["2020-01-03 10:00:00", "B", 1.0, 0.50],
        ],
        columns=["timestamp", "symbol", "adjclose", "open"],
    ).assign(timestamp=lambda df: pd.to_datetime(df["timestamp"]))

    # single column
    stocks_normalized = normalize_traces(
        stocks, "2020-01-02", values="adjclose"
    ).sort_values("symbol")
    pdt.assert_frame_equal(
        stocks_normalized, expected[["timestamp", "symbol", "adjclose"]]
    )

    # multiple columns
    stocks_normalized = normalize_traces(
        stocks, "2020-01-02", values=["adjclose", "open"]
    ).sort_values("symbol")
    pdt.assert_frame_equal(stocks_normalized, expected)

    # random order
    stocks_shuffled = stocks.sample(frac=1, ignore_index=True)
    expected_shuffled = stocks_shuffled.drop(["adjclose", "open"], axis=1).merge(
        expected, on=["timestamp", "symbol"]
    )
    stocks_shuffled_normalized = normalize_traces(
        stocks_shuffled, "2020-01-02", values=["adjclose", "open"]
    )
    # display(stocks_shuffled, stocks_shuffled_normalized)
    pdt.assert_frame_equal(stocks_shuffled_normalized, expected_shuffled)


def test_normalize_traces_to():
    stocks_long = pd.DataFrame(
        [
            [2**1, None, None],
            [None, 3**2, None],
            [None, None, 5**3],
            [None, 3**4, 5**4],
            [2**5, 3**5, 5**5],
            [2**6, 3**6, 5**6],
        ],
        columns=["A", "B", "C"],
    ).assign(
        timestamp=lambda df: pd.to_datetime("2022-01-01")
        + pd.to_timedelta(np.arange(len(df)), unit="d")
    )
    stocks = (
        stocks_long.melt(id_vars="timestamp", var_name="symbol", value_name="close")
        .dropna()
        .assign(open=lambda df: df["close"] / 10)
    )

    # stocks.pivot_table(index="timestamp", columns="symbol", values="close").fillna("")

    stocks_relative = normalize_traces(stocks)
    pdt.assert_frame_equal(
        stocks_relative.pivot_table(
            index="timestamp", columns="symbol", values="close"
        ),
        stocks_long.set_index("timestamp") / np.array([[2**1, 3**2, 5**3]]) - 1,
        check_names=False,
    )

    stocks_relative = normalize_traces(stocks, "2022-01-04")
    pdt.assert_frame_equal(
        stocks_relative.pivot_table(
            index="timestamp", columns="symbol", values="close"
        ),
        stocks_long.set_index("timestamp") / np.array([[2**5, 3**4, 5**4]]) - 1,
        check_names=False,
    )

    stocks_relative = normalize_traces(stocks, "2022-01-05")
    pdt.assert_frame_equal(
        stocks_relative.pivot_table(
            index="timestamp", columns="symbol", values="close"
        ),
        stocks_long.set_index("timestamp") / np.array([[2**5, 3**5, 5**5]]) - 1,
        check_names=False,
    )

    # display(
    #     stocks_relative.pivot_table(
    #         index="timestamp", columns="symbol", values="close"
    #     ).fillna("")
    # )


if __name__ == "__main__":
    import inspect

    tests = {
        k: v
        for k, v in dict(globals()).items()
        if k.startswith("test_") and inspect.isfunction(v)
    }
    for k, v in tests.items():
        print(f"Testing {k} ..")
        v()
