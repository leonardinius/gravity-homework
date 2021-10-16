import asyncio
import os
from dotenv import load_dotenv

from binance import BinanceSocketManager
from binance.client import AsyncClient

load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')


async def main():
    print('Binance API Key: %s...%s' % (API_KEY[:3], API_KEY[-3:]))
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.trade_socket('BTCUSDT')
    # then start receiving messages
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)

    await client.close_connection()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
