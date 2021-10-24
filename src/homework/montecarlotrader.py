import logging
import time
from decimal import Decimal
from typing import Tuple, Set, Dict

from homework.testorder import TestOrder, Side
from homework.timewindow import SlidingWindow


class MonteCarloTrader:
    _window: SlidingWindow[TestOrder]
    _precision: int
    _spreads: Set[Decimal]

    def __init__(self, window: SlidingWindow[TestOrder], time_function=time.time, precision: int = 13) -> None:
        self._window = window
        self._time = time_function
        self._precision = precision
        self._spreads = set()

    def tick_place_order(self,
                         spread: Decimal,
                         best_bid_price: Decimal,
                         best_ask_price: Decimal,
                         ) -> None:
        placed_at = self._time()
        bid_oder = TestOrder(
            placed_at=placed_at,
            side=Side.BID,
            spread=spread,
            price=Side.BID.price_with_spread(spread, best_bid_price, self._precision),
        )
        ask_oder = TestOrder(
            placed_at=placed_at,
            side=Side.ASK,
            spread=spread,
            price=Side.ASK.price_with_spread(spread, best_ask_price, self._precision),
        )
        self._window.put(placed_at, ask_oder)
        self._window.put(placed_at, bid_oder)
        self._spreads.add(spread)

    def spreads(self) -> Set[Decimal]:
        return self._spreads.copy()

    def precision(self) -> int:
        return self._precision

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
        all_spreads = self._spreads

        all_counters: Dict[Decimal, Tuple[int, int]] = dict()
        for _time, order in all_orders:
            for spread in all_spreads:
                counter = all_counters.get(spread, (0, 0))
                if order.fulfilled \
                        and spread.is_signed() == order.spread.is_signed() \
                        and spread.__abs__() <= order.spread.__abs__():
                    bid_counter, ask_counter = counter
                    if order.side == Side.BID:
                        bid_counter += 1
                    if order.side == Side.ASK:
                        ask_counter += 1
                    counter = (bid_counter, ask_counter)
                all_counters[spread] = counter

        side_size = int(len(all_orders) / 2)
        percentages: Dict[Decimal, Tuple[float, float]] = dict()
        for spread in all_spreads:
            bid_matched, ask_matched = all_counters[spread]
            percentage = (
                bid_matched / side_size,
                ask_matched / side_size
            )
            percentages[spread] = percentage

        return percentages

    def select_best_spread(self, threshold: float):
        thresholds = self.calculate_percentile_thresholds()
        by_percentages_bid = sorted(thresholds.items(), key=lambda item: -1 * item[1][0])
        by_percentages_ask = sorted(thresholds.items(), key=lambda item: -1 * item[1][1])
        best_bid = (by_percentages_bid[0][0], by_percentages_bid[0][1][0])
        best_ask = (by_percentages_ask[0][0], by_percentages_ask[0][1][1])
        logging.info(f'select_best_spread len={self._window.len()} best_bid={best_bid!r} best_ask={best_ask!r}')

        percentages = sorted(thresholds.items(), key=lambda item: -1 * item[0])
        bid = next(filter(lambda item: item[1][0] >= threshold, percentages), (None, []))
        ask = next(filter(lambda item: item[1][1] >= threshold, percentages), (None, []))
        return bid[0], ask[0],
