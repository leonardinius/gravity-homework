import asyncio
import logging
import os

from dotenv import load_dotenv

from mainapp import MainApp

load_dotenv()

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('websockets').setLevel(logging.WARNING)

API_KEY = os.environ['BINANCE_API_KEY']
API_SECRET = os.environ['BINANCE_API_SECRET']
SYMBOL_PAIR = os.getenv('SYMBOL_PAIR', 'BTCUSDT')

MAIN_APP = MainApp(API_KEY, API_SECRET, SYMBOL_PAIR)


async def main() -> int:
    await MAIN_APP.run()
    return 0


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
