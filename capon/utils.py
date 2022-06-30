import numpy as np
import pandas as pd


def normalize_values(stocks, anchor, values="adjclose", baseline=1):
    values = listify(values)

    stocks_ts = stocks.assign(
        date=lambda df: pd.to_datetime(
            df["timestamp"].apply(lambda dt: dt.tz_localize(None).date())
        )
    ).pivot_table(index="date", columns="symbol", values=values)

    anchor_close = stocks_ts.loc[anchor:].bfill().iloc[0]

    # stocks_ts_normed = (stocks_ts / anchor_close - baseline) \
    #     .reset_index().melt(id_vars='date', value_name=values)
    stocks_ts_normed = (stocks_ts / anchor_close - baseline).stack(-1).reset_index()
    return stocks_ts_normed


def listify(x):
    x = [x] if np.ndim(x) == 0 else x
    return x


def normalize_traces(
    traces,
    to="start",
    index="timestamp",
    values=None,
    by="symbol",
    method="independent",
    baseline=1,
):
    if to == "start":
        if method == "independent":
            to = traces[index].min()
        elif method == "common":
            raise NotImplementedError
        else:
            raise ValueError(f'unknown method "{method}"')

    if values is None:
        values = traces.select_dtypes(np.number).columns.tolist()
    normalized = (
        traces.groupby(by)
        .apply(lambda g: g[values] / g[g[index] >= to].iloc[0][values] - baseline)
        .astype(np.number)
    )

    return traces[[index, by]].join(normalized)
