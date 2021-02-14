import plotly.express as px

from capon.utils import normalize_values


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

    stocks_ts_normed = normalize_values(stocks, anchor)

    fig = px.line(stocks_ts_normed, x='date', y='adjclose', color='symbol',
                  title=f'{title}: Historical changes from {anchor}')
    fig.update_layout(yaxis_tickformat='+%')
    fig.update_layout(shapes=[
        dict(
            type='line',
            yref='paper', y0=0, y1=1,
            xref='x', x0=anchor, x1=anchor,
            line=dict(width=1.5, dash='dash', color='rgba(0,0,0,0.5)'),
        )
    ])
    # fig.update_xaxes(rangeslider_visible=True)
    # fig.update_layout(hovermode="x")

    return fig