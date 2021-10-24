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
