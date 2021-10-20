import time
from decimal import Decimal, localcontext
from typing import Tuple

from homework.testorder import TestOrder, Side
from homework.timewindow import SlidingWindow


class MonteCarloTrader:
    _window: SlidingWindow[TestOrder]
    _precision: int

    # precision = '62478.89000000'
    #              12345.67890123
    def __init__(self, window: SlidingWindow[TestOrder], time_function=time.time, precision: int = 13) -> None:
        self._window = window
        self._time = time_function
        self._precision = precision

    def tick_place_order(self,
                         price_depth: Decimal,
                         best_bid_price: Decimal,
                         best_ask_price: Decimal,
                         ) -> None:
        placed_at = self._time()
        with localcontext() as ctx:
            ctx.prec = self._precision
            ask_oder = TestOrder(
                placed_at=placed_at,
                side=Side.ASK,
                price_depth=price_depth,
                price=best_ask_price + (best_ask_price * price_depth),
            )
            bid_oder = TestOrder(
                placed_at=placed_at,
                side=Side.BID,
                price_depth=price_depth,
                price=best_bid_price - best_bid_price * price_depth,
            )
        self._window.put(placed_at, ask_oder)
        self._window.put(placed_at, bid_oder)

    def tick_observe_trade(self, price: Decimal) -> None:
        for _time, order in self._window.pack():
            if not order.fulfilled:
                if order.side == Side.BID and price <= order.price:
                    order.fulfilled = True
                if order.side == Side.ASK and price >= order.price:
                    order.fulfilled = True

    def calculate_percentage(self,
                             side: Side,
                             price_depth: Decimal) -> float:
        side_total = 0
        depth_fulfilled_match = 0
        for _time, order in self._window.pack():
            if order.side == side:
                side_total += 1
                if order.fulfilled \
                        and price_depth.is_signed() == order.price_depth.is_signed() \
                        and price_depth.__abs__() <= order.price_depth.__abs__():
                    depth_fulfilled_match += 1
        return depth_fulfilled_match / side_total

    def select_best_depth(self,
                          percentile_threshold: float,
                          percentages: list[Tuple[Decimal, list[Decimal]]]):
        percentages = sorted(percentages, key=lambda item: - item[0])
        bid = next(filter(lambda item: item[1][0] >= percentile_threshold, percentages), (None, []))
        ask = next(filter(lambda item: item[1][1] >= percentile_threshold, percentages), (None, []))
        return bid[0], ask[0],
