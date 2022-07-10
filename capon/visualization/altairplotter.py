import altair as alt
from capon.preprocessing import normalize_traces


def plot_history(
    stocks, normalize=None, index="timestamp", value="close", by="symbol", point=False
):
    value_params = {}

    if normalize is not None:
        if normalize == "start":
            normalize = stocks[index].min()
        stocks = normalize_traces(stocks, to=normalize, index=index, by=by)
        value_params = dict(
            axis=dict(format="+%"),
            tooltip=dict(format="+.2%"),
        )

    line_kwargs = {}
    if point:
        line_kwargs = dict(point={"filled": False, "fill": "white"})

    highlight = alt.selection(type="single", on="mouseover", fields=[by], nearest=True)

    base = alt.Chart(stocks).encode(
        x=f"{index}:T",
        y=alt.Y(f"{value}:Q", axis=alt.Axis(**value_params.get("axis", {}))),
        color=f"{by}:N",
    )

    points = (
        base.mark_circle()
        .encode(
            opacity=alt.value(0),
            tooltip=[index, alt.Tooltip(value, **value_params.get("tooltip", {})), by],
        )
        .add_selection(highlight)
    )

    lines = base.mark_line(**line_kwargs).encode(
        # size=alt.condition(~highlight, alt.value(2), alt.value(3))
    )

    chart = points + lines

    if normalize is not None:
        rule = (
            alt.Chart(stocks[stocks[index] >= normalize].nsmallest(1, index))
            .mark_rule(color="black")
            .encode(x=f"{index}:T")
        )

        chart += rule

    return chart.properties(
        width=800,
        height=240,
        title=f"Historical Changes"
        + (f" from {normalize}" if normalize is not None else ""),
    )


if __name__ == "__main__":
    import pandas as pd
    from tqdm.auto import tqdm
    import capon

    tickers = ["BAC", "ALLY", "DFS", "SCHW"]

    history = pd.concat(
        [capon.stock(ticker, range="2y", interval="1mo") for ticker in tqdm(tickers)],
        ignore_index=True,
    )

    chart = plot_history(history)
    chart.display()

    chart = plot_history(history, normalize="start")
    chart.display()

    chart.configure_line(point={"filled": False, "fill": "white"}).display()

    normalize = history["timestamp"].unique()[12].strftime("%Y-%m-%d")

    chart = plot_history(
        history,
        normalize=normalize,
        point=True,
    )
    chart.display()


if __name__ == "__main__":
    from capon.datasets import load_stock_indexes

    tickers = (
        load_stock_indexes()
        .pipe(lambda df: df[df["country_code"] == "US"])
        .symbol.tolist()
    )

    stocks = pd.concat(
        [
            capon.stock(ticker, range="10y", interval="1mo").iloc[:-1]
            for ticker in tqdm(tickers)
        ],
        ignore_index=True,
    ).pipe(lambda df: df[df["timestamp"] >= "2013"])
    stocks

    capon.plot(
        stocks.merge(load_stock_indexes(), on="symbol"), by="name", normalize="start"
    )
