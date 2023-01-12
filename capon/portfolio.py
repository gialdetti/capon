import logging
import datetime
from enum import Enum
from dataclasses import dataclass, field

import pandas as pd
from tqdm.auto import tqdm

import capon


logger = logging.getLogger(__name__)
default_indexes = ["^GSPC", "^DJI", "^IXIC", "^RUT"]
local_tz = datetime.datetime.now().astimezone().tzinfo


@dataclass
class Lot:
    """
    Attributes
    ----------
    timestamp : str
        Trade date
    symbol : str
        The stock symbol
    quantity : int
        The amount of stocks
    price: float
        Cost per share
    """

    timestamp: str
    symbol: str
    quantity: int
    price_buy: float
    active: bool = 1

    def __post_init__(self):
        self.timestamp = pd.to_datetime(self.timestamp)


# pd.DataFrame([Lot("2020-01-01", "A", 100, 1.00)])
# pd.DataFrame([Lot(pd.to_datetime("2020-01-01"), "A", 100, 1.00)])


class OrderType(Enum):
    BUY = 1
    SELL = 2


@dataclass
class Order:
    """Base class for Buy/Sell orders."""

    timestamp: str
    symbol: str
    quantity: int
    price: float
    type: OrderType

    def __post_init__(self):
        self.timestamp = pd.to_datetime(self.timestamp)


# print(Order("2020-01-01", "AAA", 10, 1.23, OrderType.BUY).type)


@dataclass
class BuyOrder(Order):
    type: OrderType = field(default=OrderType.BUY, init=False)


@dataclass
class SellOrder(Order):
    type: OrderType = field(default=OrderType.SELL, init=False)


# pd.DataFrame([
#     BuyOrder("2020-01-01", "AAA", 10, 1.23),
#     SellOrder("2020-01-01", "AAA", 10, 1.23),
# ])


class Portfolio:
    def __init__(self, lots=None):
        if lots is None:
            trades = pd.DataFrame()
        else:
            trades = (
                pd.DataFrame(lots)
                .assign(
                    timestamp_buy=lambda df: pd.to_datetime(df["timestamp"]),
                )
                .drop("timestamp", axis=1)
                .pipe(Portfolio.enrich)
            )
        self.trades = trades

    def status(self, history=None, timestamp_normalizer="date"):
        performance = self.performance(
            history=history, timestamp_normalizer=timestamp_normalizer
        )

        latest = (
            performance.groupby(["lot_index", "symbol"])
            .apply(
                lambda g: g.sort_values("timestamp")
                .assign(
                    timestamp=lambda df: df["timestamp"].where(
                        df["active"] == 1, df["timestamp_sell"]
                    ),
                    price=lambda df: df["price"].where(
                        df["active"] == 1, df["price_sell"]
                    ),
                )
                .assign(
                    value=lambda df: df["price"] * df["quantity"],
                    gain=lambda df: df["value"] - df["cost"],
                    gain_pct=lambda df: df["value"] / df["cost"] - 1,
                )
                .drop(["timestamp_sell", "price_sell"], axis=1)
                .assign(daily_pct=lambda df: df["price"].pct_change())
                .tail(1)
            )
            .reset_index(drop=True)
        )
        return latest

    def performance(self, history=None, timestamp_normalizer="date", end_time=None):
        price = "adjclose"

        if timestamp_normalizer == "date":
            timestamp_normalizer = lambda ts: pd.to_datetime(ts.dt.date)
        else:
            raise NotImplementedError

        if history is None:
            history = self.fetch_history()
        # @todo, verify coverage of lots

        performance = (
            self.trades.assign(
                timestamp_buy=lambda df: timestamp_normalizer(df["timestamp_buy"])
            )
            .merge(
                history[["symbol", "timestamp", price]]
                .rename({price: "price"}, axis=1)
                .assign(timestamp=lambda df: timestamp_normalizer(df["timestamp"])),
                on="symbol",
                how="left",
            )
            .assign(
                value=lambda df: df["price"] * df["quantity"],
                gain=lambda df: df["value"] - df["cost"],
                gain_pct=lambda df: df["value"] / df["cost"] - 1,
            )
            .pipe(lambda df: df[df["timestamp_buy"] <= df["timestamp"]])
            .assign(
                active=lambda df: df["timestamp_sell"].isna()
                | (df["timestamp"] <= df["timestamp_sell"])
            )
            .astype({"active": int})
            #             .assign(timestamp_last=lambda df: df[["timestamp_sell", "timestamp"]].min(axis=1))
            #             .pipe(lambda df: df[df["timestamp"]<=df["timestamp_last"]])
            #             .drop(["timestamp_last"], axis=1)
        )

        if end_time is not None:
            performance = performance.pipe(lambda df: df[df["timestamp"] <= end_time])

        return performance

    def buy(self):
        raise NotImplementedError

    def sell(self, timestamp, symbol, quantity, price):
        assert quantity > 0

        available_lots = self.trades.pipe(lambda df: df[df["symbol"] == symbol])
        available_quantity = available_lots["quantity"].sum()
        if available_quantity < quantity:
            raise ValueError(
                f"Insufficient stocks, {quantity} were ordered to be sold, but only {available_quantity} are available."
            )

        if len(available_lots) > 1:
            raise NotImplementedError

        self.trades = (
            pd.concat(
                [
                    self.trades.assign(
                        fifo_sell_quantity=lambda df: (df["symbol"] == symbol)
                        * quantity,
                        quantity=lambda df: df["quantity"] - df["fifo_sell_quantity"],
                    )
                    .drop("fifo_sell_quantity", axis=1)
                    .pipe(lambda df: df[~(df["active"] & (df["quantity"] == 0))]),
                    available_lots.iloc[:1].assign(
                        quantity=quantity,
                        active=0,
                        timestamp_sell=timestamp,
                        price_sell=price,
                    ),
                ],
                ignore_index=True,
            )
            .assign(timestamp_sell=lambda df: pd.to_datetime(df["timestamp_sell"]))
            .pipe(Portfolio.enrich)
        )

    def fetch_history(self, symbols=None, start_time=None, end_time=None, tz=None):
        if symbols is None:
            symbols = self.trades["symbol"].unique().tolist()
        if start_time is None:
            start_time = str(self.trades["timestamp_buy"].dt.date.min())
        if end_time is None:
            end_time = str(pd.Timestamp.now().date() + pd.Timedelta(days=1))  # tomorrow

        history = pd.concat(
            [
                capon.stock(
                    symbol, start_date=start_time, end_date=end_time, interval="1d"
                ).dropna()
                for symbol in tqdm(symbols)
            ],
            ignore_index=True,
        )

        if tz is not False:
            tz = local_tz if tz is None else tz
            logger.debug(f"Setting timezone to {tz}..")

            history = history.assign(
                timestamp=lambda df: pd.to_datetime(
                    df["timestamp"], utc=True
                ).dt.tz_convert(tz)
            )

        return history

    @staticmethod
    def enrich(trades):
        trades = (
            trades.assign(
                cost=lambda df: df["price_buy"] * df["quantity"],
            )
            .sort_values(["timestamp_buy", "symbol", "active"], ignore_index=True)
            .assign(lot_index=lambda df: range(len(df)))
        )

        if "timestamp_sell" not in trades:
            assert "price_sell" not in trades
            trades = trades.assign(
                timestamp_sell=lambda df: pd.to_datetime([None] * len(df)),
                price_sell=None,
            )

        return trades

    @staticmethod
    def from_lots(lots):
        return Portfolio(lots)

    @staticmethod
    def from_orders(orders, init_lots=None):
        portfolio = Portfolio(init_lots)

        for order in orders:
            if order.type == OrderType.BUY:
                portfolio.buy(**order.__dict__)
            elif order.type == OrderType.SELL:
                portfolio.sell(**order.__dict__)
            else:
                raise ValueError(order)

        return portfolio
