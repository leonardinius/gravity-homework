from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Side(Enum):
    ASK = 1
    BID = 2

    # def diff_ratio(self, best_price: Decimal, order_price: Decimal):
    #     if self == Side.BID:
    #         return - (order_price - best_price) / best_price
    #     if self == Side.ASK:
    #         return (best_price - order_price) / best_price
    #     raise RuntimeError('Logic exception')


@dataclass
class TestOrder:
    placed_at: float
    side: Side
    price: Decimal
    # quantity: Decimal
    price_depth: Decimal
    fulfilled: bool = False
