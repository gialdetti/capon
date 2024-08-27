import capon

try:
    import plotly.io as pio

    def test_template_registration():
        assert "capon" in pio.templates

except ModuleNotFoundError as e:
    print(e)
