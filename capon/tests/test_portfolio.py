import numpy.testing as npt
from capon import Portfolio, Lot


def test_cost():
    my_portfolio = Portfolio([
        Lot('2020-03-20', 'AMZN',   2, 1888.86),
        Lot('2020-03-23', 'GOOGL',  3, 1037.89),
        Lot('2020-03-27', 'ZM',    20,  150.29),
    ])

    lots = my_portfolio.lots
    assert len(lots) == 3

    npt.assert_array_equal(lots['cost'], lots['quantity']*lots['price'])


def test_status():
    my_portfolio = Portfolio([
        Lot('2020-03-20', 'AMZN',   2, 1888.86),
        Lot('2020-03-23', 'GOOGL',  3, 1037.89),
        Lot('2020-03-27', 'ZM',    20,  150.29),
    ])

    my_portfolio.status()


def test_status_with_multiple_timezones():
    tz_portfolio = Portfolio([
        Lot('2020-01-01', '3690.HK', 1, 10),
        Lot('2020-01-01', 'RATI-L.TA', 2, 20),
        Lot('2020-01-01', 'LHA.DE', 3, 30),
        Lot('2020-01-01', 'IVR', 4, 40),
    ])

    performance = tz_portfolio.performance()
    print(performance.dtypes)

    status = tz_portfolio.status()
    print(status[['timestamp_buy', 'symbol', 'timestamp', 'price']])
