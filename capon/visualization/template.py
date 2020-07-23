import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px


pio.templates['capon'] = go.layout.Template(
    layout=go.Layout(
        font=dict(color='#887e7d'),
        paper_bgcolor='#fff1e5',
        plot_bgcolor='#fff1e5',

        title=dict(
            font=dict(size=22, color='black', family='Palatino'),
            xanchor='left',
            x=0.05),

        colorway=px.colors.qualitative.T10,

        colorscale={
            'sequential': 'Geyser_r',
            'sequentialminus': 'Geyser_r',
        }
    ),

    data_scatter=[
        go.Scatter(line=dict(width=2.5))
    ],

)

# https://plotly.com/python/builtin-colorscales/
# https://plotly.com/python/discrete-color/


# from plotly.offline import plot
# fig = px.line(x=[1,2,3], y=[1,3,2], title='Test', template='capon')
# plot(fig)