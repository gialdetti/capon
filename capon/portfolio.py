import typing

import pandas as pd

from capon.backends import yahoo as yf


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


# lots = [
#     Lot('2020-03-20', 'AMZN',  10, 1.1),
#     Lot('2020-03-20', 'TSLA',  20, 2.2),
#     Lot('2020-03-23', 'GOOGL', 30, 3.3),
#     Lot('2020-03-27', 'ZM',    40, 4.4),
# ]
# pd.DataFrame(lots)

default_indexes = ['^GSPC', '^DJI', '^IXIC', '^RUT']


class Portfolio():
    def __init__(self, lots):
        lots = pd.DataFrame(lots) \
            .assign(timestamp=lambda df: pd.to_datetime(df['timestamp']))
        lots['cost'] = lots['cost'].where(lots['cost'].notna(), lots['price']*lots['quantity']) \
            .astype({'cost': float})
        # display(lots)

        self.lots = lots



    def status(self):
        performance = self.performance()
        latest = performance.groupby('symbol').apply(lambda g: g.nlargest(1, 'timestamp')).reset_index(drop=True)
        return latest

    def performance(self, indexes=None):
        indexes = indexes or default_indexes
        print(indexes)

        history = pd.concat([yf.stock(symbol, range='1y', interval='1d').dropna()
                             for symbol in self.lots['symbol']], sort=False)

        dfh = history.assign(timestamp=lambda df: pd.DatetimeIndex(df['timestamp']).normalize().shift(16, freq='h'))
        dfo = self.lots.assign(timestamp=lambda df: pd.DatetimeIndex(df['timestamp']).normalize().shift(12, freq='h'))

        performance = dfo.merge(dfh[['symbol', 'timestamp', 'adjclose']].rename({'adjclose': 'price'}, axis=1),
                                on='symbol', suffixes=('_buy', '')) \
            .assign(value=lambda df: df['price']*df['quantity']) \
            .assign(
                gain=lambda df: df['value']-df['cost'],
                gain_pct=lambda df: df['value']/df['cost']-1
            )
        performance = performance[performance['timestamp_buy']<=performance['timestamp']]

        return performance


if False:
    my_portfolio = Portfolio([
        Lot('2020-03-20', 'AMZN',   2, 1888.86),
        Lot('2020-03-20', 'TSLA',   8,  451.40),
        Lot('2020-03-23', 'GOOGL',  3, 1037.89),
        Lot('2020-03-27', 'ZM',    20,  150.29),
    ])


if False: # DEBUG
    my_portfolio.status().sort_values('pct_change').plot.bar()
    my_portfolio.performance().plot()

    lots = my_portfolio.lots
    performance = my_portfolio.performance()


    df = lots.assign(timestamp=lambda df: df['timestamp'].dt.date) \
        .merge(
            history.assign(timestamp=lambda df: df['timestamp'].dt.date), 
            on=['timestamp', 'symbol'])

    df.assign(average=lambda df: (df['high']+df['low'])/2)[['timestamp', 'symbol', 'average']]





