import numpy as np
import pandas as pd


def normalize_values(stocks, anchor, values='adjclose', baseline=1):
    values = listify(values)

    stocks_ts = stocks \
        .assign(date=lambda df: pd.to_datetime(df['timestamp'].apply(lambda dt: dt.tz_localize(None).date()))) \
        .pivot_table(index='date', columns='symbol', values=values)

    anchor_close = stocks_ts.loc[anchor:].bfill().iloc[0]

    # stocks_ts_normed = (stocks_ts / anchor_close - baseline) \
    #     .reset_index().melt(id_vars='date', value_name=values)
    stocks_ts_normed = (stocks_ts / anchor_close - baseline) \
            .stack(-1).reset_index()
    return stocks_ts_normed


def listify(x):
    x = [x] if np.ndim(x)==0 else x
    return x


