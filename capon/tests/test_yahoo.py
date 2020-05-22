import pandas as pd
import numpy.testing as npt

from capon.backends.yahoo import get_stock, stock


def test_get_stock_tz():
    hk = stock('3690.HK')
    npt.assert_array_equal(hk['timestamp'], hk['timestamp'].dt.tz_localize(None).dt.tz_localize('Asia/Hong_Kong'))

    de = stock('LHA.DE')
    npt.assert_array_equal(de['timestamp'], de['timestamp'].dt.tz_localize(None).dt.tz_localize('Europe/Berlin'))

    # import pytz
    # pytz.country_timezones('HK')


if False:
    stocks_dict = {tick: stock(tick) for tick in ['3690.HK', 'RATI-L.TA', 'LHA.DE', 'IVR']}
    stocks = pd.concat(stocks_dict.values())


    print(stocks_dict['3690.HK']['timestamp'].dtype)
    print(stocks_dict['3690.HK']['timestamp'].nlargest(3))

    print(stocks['timestamp'].dtype)
    print(stocks['timestamp'].nlargest(3))
    print(stocks[stocks['symbol']=='3690.HK']['timestamp'].nlargest(3))


# jo = get_stock('IVR')
# jo = get_stock('RATI-L.TA')
#
# result = jo['chart']['result'][0]
# metadata = result['meta']
# ts = pd.DataFrame({
#     'timestamp': pd.to_datetime(result.get('timestamp', []), unit='s') + pd.Timedelta(metadata['gmtoffset'], unit='s'),
#     'symbol': metadata['symbol'],
#     'currency': metadata['currency'],
# })
# quote = pd.DataFrame(result['indicators']['quote'][0])
# adjclose = pd.DataFrame(result['indicators']['adjclose'][0]) if 'adjclose' in result['indicators'] else None
#
# # len(ts), len(quote), len(adjclose)
# stock = pd.concat([ts, quote, adjclose], axis=1)
#
#
# stock['timestamp'].dt.tz_localize(metadata['gmtoffset'])
#
# pd.to_datetime(result.get('timestamp', []), unit='s').tz_localize('UTC').tz_convert(metadata['gmtoffset'])