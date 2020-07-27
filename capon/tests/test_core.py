import capon


def test_adjclose():
    amd_daily = capon.stock('AMD', range='1mo', interval='1d')
    assert 'adjclose' in amd_daily

    amd_minutely = capon.stock('AMD', range='1d', interval='2m')
    assert 'close' in amd_minutely


def test_index():
    sp500 = capon.stock('^GSPC')
    assert len(sp500) > 0


def test_metadata():
    metadata = capon.metadata('AMD')
    assert metadata['symbol'] == 'AMD'
