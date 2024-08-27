import logging
import os

import pandas as pd
from tqdm.auto import tqdm
from joblib import Parallel, delayed

from capon.preprocessing import listify

from .backends.yahoo import stock


logger = logging.getLogger(__name__)


def stock_wrapped(ticker, errors="ignore", *args, **kwargs):
    """Fetch stock history, w/o exception handling.

    Parameters
    ----------
    ticker : str
        Stock ticker.
    errors : {'ignore', 'raise'}, default 'ignore'
        If 'ignore', suppress error and only existing labels are dropped.

    Returns
    -------
    DataFrame
        Stock quotes.

    Raises
    ------
    ValueError
        _description_
    """

    logger.debug(
        f"#{os.getpid()}: stock_wrapped({ticker}, {args}, {', '.join('{0}={1!r}'.format(k, v) for k, v in kwargs.items())}) starts.."
    )

    try:
        return stock(ticker, *args, **kwargs)
    except Exception as e:
        logger.warning(e)
        if errors == "raise":
            raise ValueError(f"symbol '{ticker}' couldn't be retrieved!")
    return None


def stocks(
    symbols,
    range="1d",
    interval=None,
    start=None,
    end=None,
    timestamp_normalizer="auto",
    n_jobs=None,
    *args,
    **kwargs,
):
    symbols = listify(symbols)
    assert len(set(symbols)) == len(symbols), "tickers contains duplicated symbols"

    n_jobs = 1 if n_jobs is None else n_jobs
    if n_jobs != 1:
        quotes_list = Parallel(n_jobs=-1)(
            delayed(stock_wrapped)(
                ticker, range=range, interval=interval, start=start, end=end
            )
            for ticker in tqdm(symbols)
        )
    else:
        quotes_list = [
            stock_wrapped(ticker, range=range, interval=interval, start=start, end=end)
            for ticker in tqdm(symbols)
        ]

    quotes = pd.concat(quotes_list, ignore_index=True)
    # quotes = quotes.dropna(subset=["close", "adjclose"], how="all")
    if timestamp_normalizer == "auto":
        full_days = (
            quotes.groupby(["symbol"])["timestamp"]
            .apply(pd.to_datetime)
            .diff()
            .dt.total_seconds()
            .dropna()
            .pipe(lambda s: (s / (24 * 3600) == (s / (24 * 3600)).astype(int)).all())
        )
        if full_days:
            timestamp_normalizer = "date"

    if timestamp_normalizer == "date":
        quotes = quotes.assign(
            # For multiple timezones
            timestamp=lambda df: pd.to_datetime(df["timestamp"], utc=True)
        ).assign(
            timestamp=lambda df: pd.to_datetime(df["timestamp"].dt.date),
            # timestamp=lambda df: df["timestamp"]
            # .dt.tz_localize(None)
            # .dt.normalize()
        )

    missing_symbols = set(symbols) - set(quotes["symbol"].unique())
    if missing_symbols:
        logger.debug(
            f"{len(missing_symbols):,} symbols were not found ({', '.join(missing_symbols)})"
        )

    return quotes
