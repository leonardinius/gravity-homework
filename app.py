import asyncio
import decimal
import logging
import os

from binance import BinanceSocketManager
from binance.client import AsyncClient
from binance.streams import ReconnectingWebsocket
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('websockets').setLevel(logging.WARNING)

API_KEY = os.environ['BINANCE_API_KEY']
API_SECRET = os.environ['BINANCE_API_SECRET']
SYMBOL_PAIR = os.getenv('SYMBOL_PAIR', 'BTCUSDT')

best_ask_price = decimal.Decimal()
best_bid_price = decimal.Decimal()

async def handle_ticker(ticker_stream: ReconnectingWebsocket) -> None:
    async with ticker_stream as stream:
        while True:
            res = await stream.recv()
            logging.debug(f'TICKER/JSON  {res!r}')

            global best_ask_price
            global best_bid_price
            best_ask_price = decimal.Decimal(res['a'])
            best_bid_price = decimal.Decimal(res['b'])
            spread = (best_ask_price - best_bid_price).__abs__()
            logging.debug(f'TICKER/PRICE ask={best_ask_price!r} bid={best_bid_price!r} spread={spread!r}')


async def handle_trades(trades_stream: ReconnectingWebsocket) -> None:
    async with trades_stream as stream:
        while True:
            res = await stream.recv()
            logging.debug(f'TRADE/JSON {res!r}')

            global best_ask_price
            global best_bid_price
            price = decimal.Decimal(res['p'])
            ask_spread = best_ask_price.__sub__(price)
            bid_spread = best_bid_price.__sub__(price)
            logging.debug(f'TRADE/PRICE price={price!r} ask_spread={ask_spread!r} bid_spread={bid_spread!r}')


async def main() -> int:
    logging.info('Binance API Key: %s...%s' % (API_KEY[:3], API_KEY[-3:]))
    logging.info(f'Symbol pair: {SYMBOL_PAIR}')
    binance_api_client = await AsyncClient.create()
    binance_ws = BinanceSocketManager(binance_api_client)

    symbol_ticker_socket = binance_ws.symbol_book_ticker_socket(SYMBOL_PAIR)
    trade_socket = binance_ws.trade_socket(SYMBOL_PAIR)
    await asyncio.gather(handle_ticker(symbol_ticker_socket), handle_trades(trade_socket), )

    await binance_api_client.close_connection()

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
