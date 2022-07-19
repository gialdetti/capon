import numpy as np
import pandas as pd


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
    else:
        values = listify(values)

    normalized = (
        traces.groupby(by)
        .apply(lambda g: g[values] / g[g[index] >= to].iloc[0][values] - baseline)
        .astype(np.number)
    )

    assert traces.index.nunique() == len(traces), "traces index must be unique"
    return traces[[index, by]].join(normalized)


def shift(g, index="timestamp", value="close", days=(-1, -7), fillna=None):
    assert g[index].nunique() == len(g), "{index} should be unique"
    assert all(g[[index, value]].notna())

    days = listify(days)
    s = g.set_index([index], drop=False)[[index, value]]

    windows = pd.concat(
        [s]
        + [
            s.shift(k, freq=pd.DateOffset(days=-1)).add_suffix(
                f"_{'prev' if k<0 else 'next'}{abs(k)}days"
            )
            for k in days
        ],
        axis=1,
    ).sort_index()

    if fillna is not None:
        windows = pd.concat(
            [s, windows.drop(s.columns, axis=1).fillna(method=fillna)], axis=1
        )

    windows = g.merge(
        windows.dropna(subset=[index, value]).reset_index(drop=True),
        on=[index, value],
        how="left",
        validate="one_to_one",
    )
    windows.index = g.index  # hack since merge cleans index

    return windows


if __name__ == "__main__":
    history = pd.DataFrame(
        [
            ["2014-01-27 01:00:00-04:00", 22.410451889038086],
            ["2014-02-03 01:00:00-04:00", 22.833295822143555],
            ["2014-02-10 01:00:00-04:00", 22.833295822143555],
            ["2014-02-17 01:00:00-04:00", 22.833295822143555],
            ["2014-02-24 01:00:00-04:00", 22.833295822143555],
            ["2014-03-03 01:00:00-04:00", 22.833295822143555],
            ["2014-03-10 00:00:00-04:00", 23.890390396118164],
            ["2014-03-17 00:00:00-04:00", 23.890390396118164],
            ["2014-03-24 00:00:00-04:00", 24.38370132446289],
            ["2014-03-31 00:00:00-04:00", 24.38370132446289],
            ["2014-04-07 00:00:00-04:00", 21.147573471069336],
            ["2014-04-14 00:00:00-04:00", 20.867938995361328],
            ["2014-04-21 00:00:00-04:00", 21.313613891601562],
            ["2014-04-28 00:00:00-04:00", 21.016498565673828],
        ],
        columns=["timestamp", "close"],
    ).assign(timestamp=lambda df: pd.to_datetime(df["timestamp"]))

    shift(history, days=7)
    shift(history, days=30, fillna="bfill").assign(
        d=lambda df: df["timestamp_next30days"] - df["timestamp"]
    )
