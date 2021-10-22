import asyncio
import logging
import os

from dotenv import load_dotenv

from homework.mainapp import MainApp

load_dotenv()

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('websockets').setLevel(logging.WARNING)

MAIN_APP = MainApp(
    binance_api_key=os.environ['BINANCE_API_KEY'],
    binance_api_secret=os.environ['BINANCE_API_SECRET'],
    pair=os.getenv('SYMBOL_PAIR', 'BTCUSDT')
)


async def main() -> int:
    await MAIN_APP.run()
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
