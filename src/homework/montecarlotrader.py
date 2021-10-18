import time

from testorder import TestOrder, Side
from timewindow import SlidingWindow
import decimal


class MonteCarloTrader:
    _window: SlidingWindow

    def __init__(self, window: SlidingWindow) -> None:
        self._window = window

    def tick(self,
             price_depth: decimal.Decimal,
             best_ask_price: decimal.Decimal, best_bid_price: decimal.Decimal) -> None:
        placed_at = time.time()
        ask_oder = TestOrder(
            placed_at=placed_at,
            side=Side.ASK,
            price=best_ask_price - best_ask_price * price_depth,
            price_depth=price_depth
        )
        bid_oder = TestOrder(
            placed_at=placed_at,
            side=Side.ASK,
            price=best_bid_price + best_bid_price * price_depth,
            price_depth=price_depth
        )
        self._window.put(placed_at, ask_oder)
        self._window.put(placed_at, bid_oder)
