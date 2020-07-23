"""
========================
Plotting with plotly API
========================

Plotly allows plotting data as interactive figures using javascript.
When plotting from the classic Jupyter Notebook displaying figures is easy. Simply do `fig.show()`.
When plotting from a python script the displaying is done by rendering standalone HTML files.

Here we demonstrate plotting from python script.

(see further documentation in https://plotly.com/python/getting-started/)
"""
print(__doc__)

import plotly.express as px
import capon

amd = capon.stock('AMD', range='ytd')
print(amd.head())
# amd.plot(x='timestamp', y='adjclose')

fig = px.line(amd, x='timestamp', y='adjclose', color='symbol', template='capon')
fig.write_html('my_stock.html', auto_open=True)


"""
Or, another alternatives are

1) Directly by `fig.show()`, after setting the browser as the default renderer.
```
import plotly.io as pio
pio.renderers.default = 'browser'
fig.show()
```

2) By using `plotly.offline` APIs
```
import plotly
plotly.offline.plot(fig)
```
"""