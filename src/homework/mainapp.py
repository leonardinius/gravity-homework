import asyncio
import logging
from decimal import Decimal

from binance import BinanceSocketManager
from binance.client import AsyncClient
from binance.streams import ReconnectingWebsocket

from aiotimer import Timer


class MainApp:
    _binance_api_key: str
    _binance_api_secret: str
    _pair: str
    _best_bid_price: Decimal = Decimal('0')
    _best_ask_price: Decimal = Decimal('0')

    def __init__(self, binance_api_key: str, binance_api_secret: str, pair: str) -> None:
        self._binance_api_key = binance_api_secret
        self._binance_api_secret = binance_api_secret
        self._pair = pair
        self._pair = pair

    def pair(self):
        return self._pair

    def handle_ticker(self, ticker_json) -> None:
        self._best_bid_price = Decimal(ticker_json['b'])
        self._best_ask_price = Decimal(ticker_json['a'])
        spread = self._best_ask_price - self._best_bid_price
        logging.debug(f'TICKER/PRICE bid={self._best_bid_price!r} ask={self._best_ask_price!r} spread={spread!r}')

    def handle_trades(self, trades_json) -> None:
        price = Decimal(trades_json['p'])
        bid_spread = self._best_bid_price - price
        ask_spread = self._best_ask_price - price
        logging.debug(f'TRADE/PRICE price={price!r} bid_spread={bid_spread!r} ask_spread={ask_spread!r}')

    def handle_timer_tick(self) -> None:
        pass

    async def _handle_ticker(self, ticker_stream: ReconnectingWebsocket) -> None:
        async with ticker_stream as stream:
            while True:
                res = await stream.recv()
                logging.debug(f'TICKER/JSON {res!r}')
                self.handle_ticker(res)

    async def _handle_trades(self, trades_stream: ReconnectingWebsocket) -> None:
        async with trades_stream as stream:
            while True:
                res = await stream.recv()
                logging.debug(f'TRADE/JSON {res!r}')
                self.handle_trades(res)

    async def _timer_handler(self):
        return self.handle_timer_tick()

    async def run(self) -> None:
        logging.info('Binance API Key: %s...%s' % (self._binance_api_key[:3], self._binance_api_key[-3:]))
        logging.info(f'Symbol pair: {self.pair()}')
        binance_api_client = await AsyncClient.create()
        binance_ws = BinanceSocketManager(binance_api_client)

        symbol_ticker_socket = binance_ws.symbol_book_ticker_socket(self.pair())
        trade_socket = binance_ws.trade_socket(self.pair())
        timer = Timer(0.005, self._timer_handler())

        try:
            await asyncio.gather(
                self._handle_ticker(symbol_ticker_socket),
                self._handle_trades(trade_socket),
                # timer.start(),
            )
        finally:
            await binance_api_client.close_connection()
            timer.cancel()

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
