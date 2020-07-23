import plotly.io as pio
import capon


def test_template_registration():
    assert 'capon' in pio.templates
