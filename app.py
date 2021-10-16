import os

from binance.client import AsyncClient
from flask import Flask, g

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
print('Binance API Key: %s...%s' % (API_KEY[:3], API_KEY[-3:]))

app = Flask(__name__)


async def get_binance_client():
    if 'binance_client' not in g:
        g.binance_client = await AsyncClient.create(API_KEY, API_SECRET)

    return g.binance_client


@app.teardown_appcontext
async def teardown_binance_client(exception):
    binance_client = g.pop('binance_client', None)

    if binance_client is not None:
        await binance_client.close_connection()


@app.route("/")
async def index():
    client = await get_binance_client()
    data = await client.get_exchange_info()
    return data
