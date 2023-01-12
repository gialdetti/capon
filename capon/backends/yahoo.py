"""Backend implementation for Yahoo Finance.

"""

import logging
import os
import requests
from datetime import datetime

import pandas as pd


logger = logging.getLogger(__name__)


ROOT = os.path.dirname(__file__)
valid_range_intervals = {
    "1d": "2m",
    "5d": "15m",
    "1mo": "1h",
    "3mo": "1d",
    "6mo": "1d",
    "1y": "1wk",
    "2y": "1wk",
    "5y": "1mo",
    "10y": "1mo",
    "ytd": "1d",
    "max": "1m",
}


# # 1Y (w)
# url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval=1wk&range=1y&corsDomain=finance.yahoo.com&.tsrc=finance'
# # 1Y (d)
# url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval=1d&range=1y&corsDomain=finance.yahoo.com&.tsrc=finance'
# # 1d
# url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval=2m&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance'


def get_stock(symbol, range="1d", interval=None, start_date=None, end_date=None):
    if range not in valid_range_intervals.keys():
        raise ValueError(
            f"range must be from {list(valid_range_intervals.keys())}, got '{range}'"
        )
    interval = interval or valid_range_intervals[range]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval={interval}&range={range}&corsDomain=finance.yahoo.com&.tsrc=finance"

    if (start_date is not None) and (end_date is not None):
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?region=US&lang=en-US&includePrePost=false&interval={interval}&range={range}&corsDomain=finance.yahoo.com&.tsrc=finance"
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?"
            f"region=US&lang=en-US&includePrePost=false&interval={interval}&corsDomain=finance.yahoo.com&.tsrc=finance"
            f"&period1={start_ts}&period2={end_ts}&interval={interval}"
        )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    response = requests.get(url, headers=headers)
    logger.info(f"{response.url}.. {response.status_code}")

    jo = response.json()

    if response.status_code != 200:
        logger.info(
            f'Repsonse for "{symbol}" was {response.status_code}:',
            jo["chart"]["error"]["description"],
        )

    return jo


def stock(symbol, range="1d", interval=None, start_date=None, end_date=None):
    """Get live & historical stock prices.

    Parameters
    ----------
    symbol : str
        The ticker symbol of the required stock.
    range : {'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'}, default '1d'
        Specify the timeframe for the required data.
    interval : {None, '1m', '2m', '15m', '1h', '1d', '1wk', '1mo'}, default None
        Specify the time interval for the required data.
        If None, then the default interval of the specified `range` is used.

    Returns
    -------
    DataFrame
        Listing stock price features for all timepoints in the required timeframe. Each row includes the open, high,
        low, and close price for a given timepoint. If relevant, it will also include the adjusted closing price.
    """
    jo = get_stock(
        symbol, range=range, interval=interval, start_date=start_date, end_date=end_date
    )

    result = jo["chart"]["result"][0]
    metadata = result["meta"]
    ts = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(result.get("timestamp", []), unit="s")
            .tz_localize("UTC")
            .tz_convert(metadata["gmtoffset"]),
            "symbol": metadata["symbol"],
            "currency": metadata["currency"],
        }
    )
    quote = pd.DataFrame(result["indicators"]["quote"][0])
    adjclose = (
        pd.DataFrame(result["indicators"]["adjclose"][0])
        if "adjclose" in result["indicators"]
        else None
    )

    # len(ts), len(quote), len(adjclose)
    stock = pd.concat([ts, quote, adjclose], axis=1)
    return stock


def history(symbol, start_date, end_date, interval="1mo"):
    start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?"
        f"period1={start_ts}&period2={end_ts}&interval={interval}&includeAdjustedClose=true&includePrePost=false"
    )

    # range, interval = "ytd", "1wk"
    # # range, interval = "1d", "2m"
    # range, interval = "1d", "1h"

    # url = (
    #     f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?"
    #     f"range={range}&interval={interval}&includeAdjustedClose=true&includePrePost=false"
    # )
    logger.info(url)

    history = (
        pd.read_csv(url, parse_dates=["Date"])
        .assign(symbol=symbol)
        .rename(str.lower, axis=1)
        .rename({"date": "timestamp", "adj close": "adjclose"}, axis=1)
        .set_index(["timestamp", "symbol"])
        .reset_index()
    )
    return history


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    stocks1 = history(
        "AAPL", start_date="1980-01-01", end_date="2025-01-01", interval="1wk"
    )
    stocks1

    stocks2 = stock(
        "AAPL", start_date="1980-01-01", end_date="2025-01-01", interval="1d"
    )
