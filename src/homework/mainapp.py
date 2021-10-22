import logging
from decimal import Decimal


class MainApp:
    _pair: str
    _best_bid_price: Decimal = Decimal('0')
    _best_ask_price: Decimal = Decimal('0')

    def __init__(self, pair: str) -> None:
        self._pair = pair
        self._pair = pair

    def pair(self):
        return self._pair

    async def handle_ticker(self, ticker_json) -> None:
        self._best_bid_price = Decimal(ticker_json['b'])
        self._best_ask_price = Decimal(ticker_json['a'])
        spread = self._best_ask_price - self._best_bid_price
        logging.debug(f'TICKER/PRICE bid={self._best_bid_price!r} ask={self._best_ask_price!r} spread={spread!r}')

    async def handle_trades(self, trades_json) -> None:
        price = Decimal(trades_json['p'])
        bid_spread = self._best_bid_price - price
        ask_spread = self._best_ask_price - price
        logging.debug(f'TRADE/PRICE price={price!r} bid_spread={bid_spread!r} ask_spread={ask_spread!r}')

    async def handle_timer_tick(self) -> None:
        logging.debug('Hello!')

# https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-book-ticker-streams
#
# Individual Symbol Book Ticker Streams
# Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.
#
# Stream Name: <symbol>@bookTicker
#
# Update Speed: Real-time
#
# Payload:
#
# {
#   "u":400900217,     // order book updateId
#   "s":"BNBUSDT",     // symbol
#   "b":"25.35190000", // best bid price
#   "B":"31.21000000", // best bid qty
#   "a":"25.36520000", // best ask price
#   "A":"40.66000000"  // best ask qty
# }
#
# https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#trade-streams
# The Trade Streams push raw trade information; each trade has a unique buyer and seller.
#
# Stream Name: <symbol>@trade
#
# Update Speed: Real-time
#
# Payload:

# {
#   "e": "trade",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "t": 12345,       // Trade ID
#   "p": "0.001",     // Price
#   "q": "100",       // Quantity
#   "b": 88,          // Buyer order ID
#   "a": 50,          // Seller order ID
#   "T": 123456785,   // Trade time
#   "m": true,        // Is the buyer the market maker?
#   "M": true         // Ignore
# }
