import logging
import time
from decimal import Decimal, localcontext
from typing import Tuple, Set, Dict

from homework.testorder import TestOrder, Side
from homework.timewindow import SlidingWindow


class MonteCarloTrader:
    _window: SlidingWindow[TestOrder]
    _precision: int
    _depths: Set[Decimal]

    # precision = '62478.89000000'
    #              12345.67890123
    def __init__(self, window: SlidingWindow[TestOrder], time_function=time.time, precision: int = 13) -> None:
        self._window = window
        self._time = time_function
        self._precision = precision
        self._depths = set()

    def tick_place_order(self,
                         price_depth: Decimal,
                         best_bid_price: Decimal,
                         best_ask_price: Decimal,
                         ) -> None:
        placed_at = self._time()
        with localcontext() as ctx:
            ctx.prec = self._precision
            bid_oder = TestOrder(
                placed_at=placed_at,
                side=Side.BID,
                price_depth=price_depth,
                price=Side.BID.price_with_depth(price_depth, best_bid_price),
            )
            ask_oder = TestOrder(
                placed_at=placed_at,
                side=Side.ASK,
                price_depth=price_depth,
                price=Side.ASK.price_with_depth(price_depth, best_ask_price),
            )
        self._window.put(placed_at, ask_oder)
        self._window.put(placed_at, bid_oder)
        self._depths.add(price_depth)

    def depths(self) -> Set[Decimal]:
        return self._depths.copy()

    def tick_observe_trade(self, price: Decimal) -> None:
        ts = time.time_ns()
        for _time, order in self._window.pack():
            if not order.fulfilled:
                if order.side == Side.BID and price <= order.price:
                    order.fulfilled = True
                if order.side == Side.ASK and price >= order.price:
                    order.fulfilled = True
        ts = time.time_ns() - ts
        logging.debug(f'time={ts!r}ns')

    def calculate_percentile_thresholds(self) -> Dict[Decimal, Tuple[float, float]]:
        all_orders = self._window.pack().copy()
        all_depths = self.depths()

        all_counters: Dict[Decimal, Tuple[int, int]] = dict()
        for _time, order in all_orders:
            for price_depth in all_depths:
                counter = all_counters.get(price_depth, (0, 0))
                if order.fulfilled \
                        and price_depth.is_signed() == order.price_depth.is_signed() \
                        and price_depth.__abs__() <= order.price_depth.__abs__():
                    bid_counter, ask_counter = counter
                    if order.side == Side.BID:
                        bid_counter += 1
                    if order.side == Side.ASK:
                        ask_counter += 1
                    counter = (bid_counter, ask_counter)
                all_counters[price_depth] = counter

        side_size = int(len(all_orders) / 2)
        percentages: Dict[Decimal, Tuple[float, float]] = dict()
        for price_depth in all_depths:
            bid_matched, ask_matched = all_counters[price_depth]
            percentage = (
                bid_matched / side_size,
                ask_matched / side_size
            )
            percentages[price_depth] = percentage

        return percentages

    def select_best_depth(self, threshold: float):
        percentages = sorted(self.calculate_percentile_thresholds().items(), key=lambda item: -1 * item[0])
        bid = next(filter(lambda item: item[1][0] >= threshold, percentages), (None, []))
        ask = next(filter(lambda item: item[1][1] >= threshold, percentages), (None, []))
        return bid[0], ask[0],
