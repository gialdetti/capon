import numpy as np
import pandas as pd

import numpy.testing as npt
import pandas.testing as pdt

import capon
from capon.portfolio import Portfolio, Lot


def test_cost():
    my_portfolio = Portfolio(
        [
            Lot("2020-03-20", "AMZN", 2, 1888.86),
            Lot("2020-03-23", "GOOGL", 3, 1037.89),
            Lot("2020-03-27", "ZM", 20, 150.29),
        ]
    )

    trades = my_portfolio.trades
    assert len(trades) == 3

    npt.assert_array_equal(trades["cost"], trades["quantity"] * trades["price_buy"])


def test_status():
    my_portfolio = Portfolio(
        [
            Lot("2020-03-20", "AMZN", 2, 1888.86),
            Lot("2020-03-23", "GOOGL", 3, 1037.89),
            Lot("2020-03-27", "ZM", 20, 150.29),
        ]
    )

    my_portfolio.status()


def test_performance_with_end_time():
    def assert_stats(performance, max_date, counts):
        pdt.assert_frame_equal(
            performance.groupby(["symbol"])["timestamp"].agg(["max", "count"]),
            pd.DataFrame(
                [
                    ["AMZN", max_date, counts[0]],
                    ["GOOGL", max_date, counts[1]],
                ],
                columns=["symbol", "max", "count"],
            )
            .set_index("symbol")
            .assign(max=lambda df: pd.to_datetime(df["max"])),
        )

    last_trading_days = (
        capon.stock("AMZN", range="1mo", interval="1d")["timestamp"]
        .dt.strftime("%Y-%m-%d")
        .tolist()
    )

    my_portfolio = Portfolio(
        [
            Lot(last_trading_days[-5], "AMZN", 2, 3263.38),
            Lot(last_trading_days[-4], "GOOGL", 3, 1884.15),
        ]
    )

    before_yesterday, yesterday, today = last_trading_days[-3:]

    performance = my_portfolio.performance()
    assert_stats(performance, max_date=today, counts=[5, 4])

    performance_yesterday = my_portfolio.performance(end_time=yesterday)
    assert_stats(performance_yesterday, max_date=yesterday, counts=[4, 3])

    performance_before = my_portfolio.performance(end_time=before_yesterday)
    assert_stats(performance_before, max_date=before_yesterday, counts=[3, 2])

    pdt.assert_frame_equal(
        performance_yesterday.pipe(
            lambda df: df[df["timestamp"] <= before_yesterday]
        ).reset_index(drop=True),
        performance_before.reset_index(drop=True),
    )


def test_status_with_multiple_timezones():
    tz_portfolio = Portfolio(
        [
            Lot("2020-01-01", "3690.HK", 1, 10),
            Lot("2020-01-01", "RATI-L.TA", 2, 20),
            Lot("2020-01-01", "LHA.DE", 3, 30),
            Lot("2020-01-01", "IVR", 4, 40),
        ]
    )

    performance = tz_portfolio.performance()
    print(performance.dtypes)

    status = tz_portfolio.status()
    print(status[["timestamp_buy", "symbol", "timestamp", "price_buy"]])


def test_multiple_lots_per_ticker():
    my_portfolio = Portfolio(
        [
            Lot("2020-03-20", "AMZN", 2, 1888.86),
            Lot("2020-03-23", "GOOGL", 3, 1037.89),
            Lot("2020-03-27", "ZM", 20, 150.29),
            Lot("2020-04-24", "GOOGL", 6, 1270.00),
        ]
    )

    # performance = my_portfolio.performance()

    status = my_portfolio.status()
    pdt.assert_series_equal(
        status["symbol"].value_counts(), my_portfolio.trades["symbol"].value_counts()
    )


def test_multiple_lots_per_ticker_different_time():
    my_portfolio = Portfolio(
        [
            Lot("2020-03-20", "AMZN", 2, 1888.86),
            Lot("2020-03-23 10:00:00", "GOOGL", 3, 1037.89),
            Lot("2020-04-23 10:00:01", "GOOGL", 6, 1270.00),
        ]
    )

    status = my_portfolio.status()
    pdt.assert_series_equal(
        status["symbol"].value_counts(), my_portfolio.trades["symbol"].value_counts()
    )


def _test_averaged_price():
    my_portfolio = Portfolio(
        [
            Lot("2020-03-20", "AMZN", 2, 1888.86),
            Lot("2020-03-23", "GOOGL", 1, 1037.89),
            Lot("2020-03-27", "ZM", 20, 150.29),
            Lot("2020-04-24", "GOOGL", 2, 1270.00),
            Lot("2020-04-25", "GOOGL", 3, 1280.00),
            Lot("2020-04-26", "GOOGL", 4, 1280.00),
        ]
    )

    my_portfolio.trades.sort_values("timestamp").groupby("symbol").agg(
        {
            "timestamp": "last",
            "quantity": "sum",
            "cost": "sum",
        }
    ).reset_index().assign(average_price=lambda df: df["cost"] / df["quantity"])

    # Sell
    symbol, quantity = "GOOGL", 5

    my_portfolio.trades.sort_values("timestamp")
    my_portfolio.status()

    (
        my_portfolio.trades.sort_values("timestamp")
        .query(f'symbol == "{symbol}"')["quantity"]
        .cumsum()
        - quantity
    )

    import pandas as pd

    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)


def create_history(n_symbols=3, n_days=4):
    dummy_history = pd.concat(
        [
            pd.DataFrame(
                dict(
                    timestamp=pd.date_range(
                        start="2023-01-01 09:30:00", periods=n_days, tz="-05:00"
                    ),
                    symbol=chr(65 + i),
                )
            ).assign(adjclose=lambda df: 10 ** (i) * (np.arange(len(df)) + 1))
            for i in range(n_symbols)
        ]
    )

    return dummy_history


def test_starting_from_buy_date():
    test_history = create_history()
    consecutive_lots = [
        Lot("2023-01-02", "A", 100, 1),
        Lot("2023-01-03", "B", 200, 10),
        Lot("2023-01-04", "C", 300, 100),
    ]

    performance = Portfolio(consecutive_lots).performance(history=test_history)

    actual = performance.groupby("symbol")["timestamp"].agg(["min", "max", "count"])
    expected = pd.DataFrame(
        dict(
            symbol=["A", "B", "C"],
            min=pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
            max=pd.to_datetime(["2023-01-04", "2023-01-04", "2023-01-04"]),
            count=[3, 2, 1],
        )
    ).set_index("symbol")
    pdt.assert_frame_equal(actual, expected)


def test_complete_lot():
    test_history = create_history()
    test_lots = [
        Lot("2023-01-01", "A", 100, 1),
        Lot("2023-01-01", "B", 200, 10),
        Lot("2023-01-01", "C", 300, 100),
    ]

    test_portfolio = Portfolio(test_lots)
    test_portfolio.sell("2023-01-03", "B", 200, 30)

    status = test_portfolio.status(history=test_history)

    performance = test_portfolio.performance(history=test_history)

    actual = performance.groupby(["symbol", "lot_index", "active", "quantity"])[
        "timestamp"
    ].agg(["min", "max", "count"])

    expected = (
        pd.DataFrame(
            [
                ["A", 0, 1, 100, "2023-01-01", "2023-01-04", 4],
                ["B", 1, 0, 200, "2023-01-04", "2023-01-04", 1],
                ["B", 1, 1, 200, "2023-01-01", "2023-01-03", 3],
                ["C", 2, 1, 300, "2023-01-01", "2023-01-04", 4],
            ],
            columns=[
                "symbol",
                "lot_index",
                "active",
                "quantity",
                "min",
                "max",
                "count",
            ],
        )
        .set_index(["symbol", "lot_index", "active", "quantity"])
        .assign(
            min=lambda df: pd.to_datetime(df["min"]),
            max=lambda df: pd.to_datetime(df["max"]),
        )
    )
    pdt.assert_frame_equal(actual, expected)

    (
        performance.pivot_table(
            index="timestamp",
            columns=["symbol", "lot_index", "quantity"],
            values=["value"],
        )
    )


def test_sell_partial_lot():
    test_history = create_history()
    test_lots = [
        Lot("2023-01-01", "A", 100, 1),
        Lot("2023-01-01", "B", 200, 10),
        Lot("2023-01-01", "C", 300, 100),
    ]

    test_portfolio = Portfolio(test_lots)
    test_portfolio.sell("2023-01-03", "B", 150, 31)

    status = test_portfolio.status(history=test_history)

    expected_status_b = pd.DataFrame(
        data=[
            [150, 10, 1500, 0, 31, 4650, 3150, 2.1],
            [50, 10, 500, 1, 40, 2000, 1500, 3.0],
        ],
        columns=[
            "quantity",
            "price_buy",
            "cost",
            "active",
            "price",
            "value",
            "gain",
            "gain_pct",
        ],
        index=[1, 2],
    )
    pdt.assert_frame_equal(
        status.pipe(lambda df: df[df["symbol"] == "B"])[expected_status_b.columns],
        expected_status_b,
    )

    performance = test_portfolio.performance(history=test_history)
    # npt.assert_array_equal(
    #     performance.groupby(["symbol", "active"], as_index=False).size(),
    #     pd.DataFrame([["A", 1, 4], ["B", 0, 1], ["B", 1, 7], ["C", 1, 4]])
    # )
    actual = performance.groupby(["symbol", "lot_index", "active", "quantity"])[
        "timestamp"
    ].agg(["min", "max", "count"])
    expected = (
        pd.DataFrame(
            [
                ["A", 0, 1, 100, "2023-01-01", "2023-01-04", 4],
                ["B", 1, 0, 150, "2023-01-04", "2023-01-04", 1],
                ["B", 1, 1, 150, "2023-01-01", "2023-01-03", 3],
                ["B", 2, 1, 50, "2023-01-01", "2023-01-04", 4],
                ["C", 3, 1, 300, "2023-01-01", "2023-01-04", 4],
            ],
            columns=[
                "symbol",
                "lot_index",
                "active",
                "quantity",
                "min",
                "max",
                "count",
            ],
        )
        .set_index(["symbol", "lot_index", "active", "quantity"])
        .assign(
            min=lambda df: pd.to_datetime(df["min"]),
            max=lambda df: pd.to_datetime(df["max"]),
        )
    )
    pdt.assert_frame_equal(actual, expected)

    performance_b0 = performance.merge(pd.DataFrame(dict(symbol=["B"], active=[0])))
    npt.assert_array_equal(
        performance_b0["timestamp"],
        pd.date_range("2023-01-04", periods=1),
    )
    assert (performance_b0["timestamp_sell"] == "2023-01-03").all()
    assert (performance_b0["price_sell"] == 31).all()

    performance_b1_1 = performance.merge(
        pd.DataFrame(dict(symbol=["B"], active=[1], lot_index=[1]))
    )
    npt.assert_array_equal(
        performance_b1_1["timestamp"],
        pd.date_range("2023-01-01", periods=3),
    )
    assert (performance_b1_1["timestamp_sell"] == "2023-01-03").all()
    assert (performance_b1_1["price_sell"] == 31).all()

    performance_b1_2 = performance.merge(
        pd.DataFrame(dict(symbol=["B"], active=[1], lot_index=[2]))
    )
    npt.assert_array_equal(
        performance_b1_2["timestamp"],
        pd.date_range("2023-01-01", periods=4),
    )
    assert performance_b1_2["timestamp_sell"].isna().all()
    assert performance_b1_2["price_sell"].isna().all()

    (
        performance.pivot_table(
            index="timestamp",
            columns=["symbol", "lot_index", "quantity"],
            values=["price"],
        )
    )
