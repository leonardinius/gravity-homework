import decimal
from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    ASK = 1
    BID = 2


@dataclass
class TestOrder:
    placed_at: float
    side: Side
    price: decimal.Decimal
    # quantity: decimal.Decimal
    price_depth: decimal.Decimal
    fulfilled: bool = False
