import altair as alt
from capon.preprocessing import normalize_traces


defaults = dict(line=dict(interpolate="monotone"))


def plot_history(
    stocks,
    normalize=None,
    index="timestamp",
    value="close",
    by="symbol",
    point=False,
    title="Historical Performance",
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

    line_kwargs = defaults["line"].copy()
    if point:
        line_kwargs.update(dict(point={"filled": False, "fill": "white"}))

    highlight = alt.selection(type="single", on="mouseover", fields=[by], nearest=True)

    base = alt.Chart(stocks).encode(
        x=alt.X(f"{index}:T", axis=alt.Axis(format="%Y-%m-%d"), title=None),
        y=alt.Y(
            f"{value}:Q", axis=alt.Axis(**value_params.get("axis", {})), title=None
        ),
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
        title={
            "text": title,
            "subtitle": f"Relative to {normalize}" if normalize is not None else "",
        },
    )


if __name__ == "__main__":
    import capon

    tickers = ["BAC", "ALLY", "DFS", "SCHW"]
    history = capon.stocks(tickers, range="2y", interval="1mo", n_jobs=-1)

    chart = plot_history(history)
    chart.display()

    chart = plot_history(history, normalize="start")
    chart.display()

    chart.configure_line(point={"filled": False, "fill": "white"}).display()

    normalize = history["timestamp"].unique()[12].strftime("%Y-%m-%d")
    chart = plot_history(history, normalize=normalize, point=True)
    chart.display()


if __name__ == "__main__":
    from capon.datasets import load_stock_indexes

    indices_tickers = (
        load_stock_indexes()
        .pipe(lambda df: df[df["country_code"] == "US"])
        .symbol.tolist()
    )

    indices = capon.stocks(
        indices_tickers, range="10y", interval="1mo", n_jobs=-1
    ).pipe(lambda df: df[df["timestamp"] >= "2013"])
    indices

    capon.plot(
        indices.merge(load_stock_indexes(), on="symbol"),
        by="name",
        normalize="start",
        title="Market Indices Change",
    ).configure_legend(title=None).display()
