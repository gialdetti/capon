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