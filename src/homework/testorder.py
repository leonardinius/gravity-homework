from dataclasses import dataclass
from decimal import Decimal, localcontext
from enum import Enum


class Side(Enum):
    ASK = 1
    BID = 2

    def price_with_depth(self, price_depth: Decimal, best_price: Decimal, precision: int):
        with localcontext() as ctx:
            ctx.prec = precision
            if self == Side.BID:
                return best_price - best_price * price_depth
            if self == Side.ASK:
                return best_price + best_price * price_depth
            raise RuntimeError('Logic exception')


@dataclass
class TestOrder:
    placed_at: float
    side: Side
    price: Decimal
    # quantity: Decimal
    price_depth: Decimal
    fulfilled: bool = False
