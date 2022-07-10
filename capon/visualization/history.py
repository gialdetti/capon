import plotly.express as px

from capon.preprocessing import normalize_traces


def plot_history(stocks, anchor, title=""):
    """Plot historical prices of stocks

    Parameters
    ----------
    stocks
    anchor
    title

    Returns
    -------

    """

    stocks_ts_normed = normalize_traces(stocks, to=anchor)

    fig = px.line(
        stocks_ts_normed,
        x="timestamp",
        y="adjclose",
        color="symbol",
        title=f"{title}: Historical changes from {anchor}",
    )
    fig.update_layout(yaxis_tickformat="+%")
    fig.update_layout(
        shapes=[
            dict(
                type="line",
                yref="paper",
                y0=0,
                y1=1,
                xref="x",
                x0=anchor,
                x1=anchor,
                line=dict(width=1.5, dash="dash", color="rgba(0,0,0,0.5)"),
            )
        ]
    )
    # fig.update_xaxes(rangeslider_visible=True)
    # fig.update_layout(hovermode="x")

    return fig


if __name__ == "__main__":
    import capon

    stocks = capon.stock("TSLA", range="1y")
    fig = plot_history(stocks, anchor=stocks["timestamp"].median())
    fig.show()
