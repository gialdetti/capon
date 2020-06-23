import plotly.express as px

from .common import defaults


def plot_status(status, y='gain_pct',
                template=defaults['template'], **kwargs):

    total_cost, total_value = status.sum()[['cost', 'value']]
    title = f'My Holdings; Gain of ${total_value-total_cost:,.2f} ({total_value/total_cost-1:,.2%})'

    fig = px.bar(status.sort_values(y, ascending=False),
                 x='symbol', y=y, color=y,
                 text=y, hover_data=['gain'],
                 title=title,
                 template=template, color_continuous_midpoint=0,
                 **kwargs)
    fig.update_layout(yaxis=dict(tickformat='+,.0%'), coloraxis=dict(showscale=False))
    fig.update_traces(texttemplate='%{text:+,.0%}', textposition='outside',
                      hovertemplate='<b>%{x}</b><br>%{customdata[0]:+.2f} (%{marker.color:+,.2%})')

    return fig