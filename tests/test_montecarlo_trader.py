from decimal import Decimal
from typing import Callable

from homework import timewindow
from homework.montecarlotrader import MonteCarloTrader
from homework.testorder import TestOrder


def test_smoke_test_percentage_calculations():
    # tick, system time is set to 10
    time_function: Callable[[], float] = lambda: 11.0
    # we are interested in last 5 seconds
    window = timewindow.SlidingWindow[TestOrder](5)
    window._time = time_function
    trader = MonteCarloTrader(window=window, time_function=time_function)

    # ticker price bid='62478.88000000' ask='62478.89000000'
    trader.tick_place_order(Decimal('-0.0001'), Decimal('62478.88000000'), Decimal('62478.89000000'))
    trader.tick_place_order(Decimal('-0.0002'), Decimal('62478.88000000'), Decimal('62478.89000000'))
    trader.tick_place_order(Decimal('-0.0003'), Decimal('62478.88000000'), Decimal('62478.89000000'))
    trader.tick_place_order(Decimal('0.0001'), Decimal('62478.88000000'), Decimal('62478.89000000'))
    trader.tick_place_order(Decimal('0.0002'), Decimal('62478.88000000'), Decimal('62478.89000000'))
    trader.tick_place_order(Decimal('0.0003'), Decimal('62478.88000000'), Decimal('62478.89000000'))

    # trades from the web-socket
    trader.tick_observe_trade(Decimal('62446.05000000'))
    trader.tick_observe_trade(Decimal('62478.30000000'))
    trader.tick_observe_trade(Decimal('62479.86000000'))

    percentages = trader.calculate_percentile_thresholds()
    rounded_percentages = dict((k, tuple(map(lambda x: round(x, 2), v))) for k, v in percentages.items())

    assert rounded_percentages == dict([
        # (depth ratio, [bid occurrence %, ask occurrence%])
        (Decimal('-0.0003'), (0.17, 0.17)),
        (Decimal('-0.0002'), (0.33, 0.33)),
        (Decimal('-0.0001'), (0.5, 0.5)),
        (Decimal('0.0003'), (0.17, 0.0)),
        (Decimal('0.0002'), (0.33, 0.0)),
        (Decimal('0.0001'), (0.5, 0.0))
    ])

    # assert what if we satisfied with N% occurrence, what are the depths we should shoot for?
    # N% = 30%
    assert trader.select_best_depth(0.3) == (Decimal('0.0002'), Decimal('-0.0001'))
    # N% = 50%
    assert trader.select_best_depth(0.5) == (Decimal('0.0001'), Decimal('-0.0001'))
    # N% = 70%
    assert trader.select_best_depth(0.7) == (None, None)
