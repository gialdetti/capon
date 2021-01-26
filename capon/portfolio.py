import typing
import pandas as pd
from capon.backends import yahoo as yf


default_indexes = ['^GSPC', '^DJI', '^IXIC', '^RUT']


class Lot(typing.NamedTuple):
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
    price: float
    cost: float = None


class Portfolio():
    def __init__(self, lots):
        lots = pd.DataFrame(lots) \
            .assign(timestamp=lambda df: pd.to_datetime(df['timestamp']))
        lots['cost'] = lots['cost'].where(lots['cost'].notna(), lots['price']*lots['quantity']).astype({'cost': float})
        self.lots = lots

    def status(self, anchor=None):
        performance = self.performance(anchor=anchor)
        latest = performance.groupby(['timestamp_buy', 'symbol']).apply(
            lambda g: g.sort_values('timestamp').assign(daily_pct=lambda df: df['price'].pct_change()).tail(1)).reset_index(drop=True)
        return latest

    def performance(self, indexes=None, anchor=None):
        indexes = indexes or default_indexes
        # print(indexes)

        history = pd.concat([yf.stock(symbol, range='1y', interval='1d').dropna()
                             for symbol in self.lots['symbol'].unique()], sort=False)
        if anchor is not None:
            history = history[history['timestamp'] <= anchor]

        import datetime
        current_tz = datetime.datetime.now().astimezone().tzinfo
        dfh = history
        dfo = self.lots.assign(timestamp=lambda df: df['timestamp'].dt.tz_localize(current_tz))

        performance = dfo.merge(dfh[['symbol', 'timestamp', 'adjclose']].rename({'adjclose': 'price'}, axis=1),
                                on='symbol', suffixes=('_buy', '')) \
            .assign(value=lambda df: df['price']*df['quantity']) \
            .assign(
                gain=lambda df: df['value']-df['cost'],
                gain_pct=lambda df: df['value']/df['cost']-1
            )
        performance = performance[performance['timestamp_buy']<=performance['timestamp']]

        return performance





