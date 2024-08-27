import pandas.testing as pdt

import capon


def test_adjclose():
    amd_daily = capon.stock("AMD", range="1mo", interval="1d")
    assert "adjclose" in amd_daily

    amd_minutely = capon.stock("AMD", range="1d", interval="2m")
    assert "close" in amd_minutely


def test_index():
    sp500 = capon.stock("^GSPC")
    assert len(sp500) > 0


def test_metadata():
    metadata = capon.metadata("AMD")
    assert metadata["symbol"] == "AMD"


if False:
    import logging

    from IPython.display import display

    logging.basicConfig()
    logging.getLogger("capon").setLevel(logging.DEBUG)


base_tickers = ["MSFT", "AAPL", "NVDA"]


def test_stocks():
    capon.stocks(["MSFT", "AAPL", "NVDA"])


def test_stocks_njobs():
    all_quotes = []
    for n_jobs in [None, -1]:
        quotes = capon.stocks(
            base_tickers,
            start="2020-01-01",
            end="2021-01-01",
            interval="1d",
            n_jobs=n_jobs,
        )
        all_quotes.append(quotes)

    pdt.assert_frame_equal(all_quotes[0], all_quotes[1])


def test_stocks_missing():
    missing_ticker = "BZZ"

    quotes = capon.stocks(
        base_tickers + [missing_ticker],
        start="2020-01-01",
        end="2021-01-01",
        interval="1d",
    )
    # display(quotes)
    assert (quotes["symbol"].unique() == base_tickers).all()


def test_stocks_multiple_tz():
    international_ticker = "^TA125.TA"

    for timestamp_normalizer in ["auto", None, "date"]:
        quotes = capon.stocks(
            base_tickers + [international_ticker],
            start="2020-01-01",
            end="2021-01-01",
            interval="1d",
            timestamp_normalizer=timestamp_normalizer,
        )
        # display(quotes)

        assert (
            quotes["symbol"].unique() == base_tickers + [international_ticker]
        ).all()


def test_stocks_single_ticker():
    quotes = capon.stocks(
        base_tickers[0],
        start="2020-01-01",
        end="2021-01-01",
        interval="1d",
    )

    assert (quotes["symbol"].unique() == base_tickers[0]).all()


# def test_stocks_timestamp_auto():
#     quotes_1h = capon.stocks(
#         base_tickers,
#         range="1mo",
#         interval="1h",
#         timestamp_normalizer="auto",
#     )

#     quotes_1d = capon.stocks(
#         base_tickers,
#         range="1mo",
#         interval="1d",
#         timestamp_normalizer="auto",
#     )
