import asyncio
from decimal import Decimal
import logging
import os

from binance import BinanceSocketManager
from binance.client import AsyncClient
from binance.streams import ReconnectingWebsocket
from dotenv import load_dotenv

from aiotimer import Timer

load_dotenv()

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('websockets').setLevel(logging.WARNING)

API_KEY = os.environ['BINANCE_API_KEY']
API_SECRET = os.environ['BINANCE_API_SECRET']
SYMBOL_PAIR = os.getenv('SYMBOL_PAIR', 'BTCUSDT')

best_bid_price = Decimal('0')
best_ask_price = Decimal('0')


async def handle_ticker(ticker_stream: ReconnectingWebsocket) -> None:
    async with ticker_stream as stream:
        while True:
            res = await stream.recv()
            logging.debug(f'TICKER/JSON  {res!r}')

            global best_bid_price
            global best_ask_price
            best_bid_price = Decimal(res['b'])
            best_ask_price = Decimal(res['a'])
            spread = best_ask_price - best_bid_price
            logging.debug(f'TICKER/PRICE bid={best_bid_price!r} ask={best_ask_price!r} spread={spread!r}')


async def handle_trades(trades_stream: ReconnectingWebsocket) -> None:
    async with trades_stream as stream:
        while True:
            res = await stream.recv()
            logging.debug(f'TRADE/JSON {res!r}')

            global best_bid_price
            global best_ask_price
            price = Decimal(res['p'])
            bid_spread = best_bid_price - price
            ask_spread = best_ask_price - price
            logging.debug(f'TRADE/PRICE price={price!r} bid_spread={bid_spread!r} ask_spread={ask_spread!r}')


async def timer_handler():
    logging.debug('echo!')


async def main() -> int:
    logging.info('Binance API Key: %s...%s' % (API_KEY[:3], API_KEY[-3:]))
    logging.info(f'Symbol pair: {SYMBOL_PAIR}')
    binance_api_client = await AsyncClient.create()
    binance_ws = BinanceSocketManager(binance_api_client)

    symbol_ticker_socket = binance_ws.symbol_book_ticker_socket(SYMBOL_PAIR)
    trade_socket = binance_ws.trade_socket(SYMBOL_PAIR)
    timer = Timer(0.005, timer_handler)

    try:
        await asyncio.gather(
            handle_ticker(symbol_ticker_socket),
            handle_trades(trade_socket),
            # timer.start(),
        )
    finally:
        await binance_api_client.close_connection()
        timer.cancel()
    return 0


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

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
