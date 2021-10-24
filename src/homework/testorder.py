from dataclasses import dataclass
from decimal import Decimal, localcontext
from enum import Enum


class Side(Enum):
    ASK = 1
    BID = 2

    def price_with_spread(self, spread: Decimal, best_price: Decimal, precision: int):
        with localcontext() as ctx:
            ctx.prec = precision
            if self == Side.BID:
                return best_price - spread
            if self == Side.ASK:
                return best_price + spread
            raise RuntimeError('Logic exception')


@dataclass
class TestOrder:
    placed_at: float
    side: Side
    price: Decimal
    # quantity: Decimal
    spread: Decimal
    fulfilled: bool = False
