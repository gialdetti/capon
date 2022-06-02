from dataclasses import dataclass
import numpy.testing as npt
import pandas.testing as pdt

import capon
from capon import Portfolio, Lot


def test_cost():
    my_portfolio = Portfolio(
        [
            Lot("2020-03-20", "AMZN", 2, 1888.86),
            Lot("2020-03-23", "GOOGL", 3, 1037.89),
            Lot("2020-03-27", "ZM", 20, 150.29),
        ]
    )

    lots = my_portfolio.lots
    assert len(lots) == 3

    npt.assert_array_equal(lots["cost"], lots["quantity"] * lots["price"])


def test_status():
    my_portfolio = Portfolio(
        [
            Lot("2020-03-20", "AMZN", 2, 1888.86),
            Lot("2020-03-23", "GOOGL", 3, 1037.89),
            Lot("2020-03-27", "ZM", 20, 150.29),
        ]
    )

    my_portfolio.status()


def test_performance_with_anchor():
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

    anchor1, anchor2 = last_trading_days[-2], last_trading_days[-1]

    performance1 = my_portfolio.performance(anchor=anchor1)
    performance2 = my_portfolio.performance(anchor=anchor2)

    npt.assert_array_equal(
        performance1["symbol"].value_counts()[["AMZN", "GOOGL"]], [3, 2]
    )
    npt.assert_array_equal(
        performance2["symbol"].value_counts()[["AMZN", "GOOGL"]], [4, 3]
    )

    pdt.assert_frame_equal(
        performance2[performance2["timestamp"] <= anchor1].reset_index(drop=True),
        performance1.reset_index(drop=True),
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
    print(status[["timestamp_buy", "symbol", "timestamp", "price"]])


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
        status["symbol"].value_counts(), my_portfolio.lots["symbol"].value_counts()
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
        status["symbol"].value_counts(), my_portfolio.lots["symbol"].value_counts()
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

    my_portfolio.lots.sort_values("timestamp").groupby("symbol").agg(
        {
            "timestamp": "last",
            "quantity": "sum",
            "cost": "sum",
        }
    ).reset_index().assign(average_price=lambda df: df["cost"] / df["quantity"])

    # Sell
    symbol, quantity = "GOOGL", 5

    my_portfolio.lots.sort_values("timestamp")
    my_portfolio.status()

    (
        my_portfolio.lots.sort_values("timestamp")
        .query(f'symbol == "{symbol}"')["quantity"]
        .cumsum()
        - quantity
    )

    import pandas as pd

    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)
