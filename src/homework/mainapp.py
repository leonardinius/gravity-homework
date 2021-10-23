import asyncio
import logging
from decimal import Decimal
from typing import Tuple

from binance import BinanceSocketManager
from binance.client import AsyncClient
from binance.streams import ReconnectingWebsocket

from aiotimer import Timer
from montecarlotrader import MonteCarloTrader
from testorder import TestOrder
from timewindow import SlidingWindow

REPORT_MAIN_BET_FREQUENCY_SECONDS = 2
REPORT_MAIN_BET_THRESHOLD = 0.5

TRADES_OBSERVE_TIME_WINDOWS_SECONDS = 300
TRADES_BETS_FREQUENCY_SECONDS = 50 / 1000
TRADES_DEPTH_THRESHOLDS = (Decimal('-0.0003'), Decimal('0.0003'))
TRADES_DEPTH_RATIO_STEP = Decimal('0.0001')


class MainApp:
    _binance_api_key: str
    _binance_api_secret: str
    _pair: str
    _best_bid_price: Decimal = Decimal('0')
    _best_ask_price: Decimal = Decimal('0')
    _has_init_price: bool = False
    _trader: MonteCarloTrader

    def __init__(self, binance_api_key: str, binance_api_secret: str, pair: str) -> None:
        self._binance_api_key = binance_api_key
        self._binance_api_secret = binance_api_secret
        self._pair = pair
        self._pair = pair
        self._trader = MonteCarloTrader(SlidingWindow[TestOrder](TRADES_OBSERVE_TIME_WINDOWS_SECONDS))

    def pair(self):
        return self._pair

    async def handle_ticker_payload(self, ticker_json) -> None:
        """
        :param ticker_json:
        Payload:
        {
          "u":400900217,     // order book updateId
          "s":"BNBUSDT",     // symbol
          "b":"25.35190000", // best bid price
          "B":"31.21000000", // best bid qty
          "a":"25.36520000", // best ask price
          "A":"40.66000000"  // best ask qty
        }
        :return:
        """
        self._best_bid_price = Decimal(ticker_json['b'])
        self._best_ask_price = Decimal(ticker_json['a'])
        self._has_init_price = True
        spread = self._best_ask_price - self._best_bid_price
        logging.debug(f'TICKER/PRICE bid={self._best_bid_price!r} ask={self._best_ask_price!r} spread={spread!r}')

    async def handle_trades_payload(self, trades_json) -> None:
        """
        :param trades_json:
        Payload:
        {
          "e": "trade",     // Event type
          "E": 123456789,   // Event time
          "s": "BNBBTC",    // Symbol
          "t": 12345,       // Trade ID
          "p": "0.001",     // Price
          "q": "100",       // Quantity
          "b": 88,          // Buyer order ID
          "a": 50,          // Seller order ID
          "T": 123456785,   // Trade time
          "m": true,        // Is the buyer the market maker?
          "M": true         // Ignore
        }
        :return:
        """
        price = Decimal(trades_json['p'])
        bid_spread = self._best_bid_price - price
        ask_spread = self._best_ask_price - price
        logging.debug(f'TRADE/PRICE price={price!r} bid_spread={bid_spread!r} ask_spread={ask_spread!r}')
        self._trader.tick_observe_trade(price)

    async def report_bet_for_threshlod(self, threshold: float) -> Tuple[Decimal, Decimal]:
        return Decimal(0), Decimal(0)

    async def handle_timer_tick(self) -> None:
        if self._has_init_price:
            await self._place_order_bets()
        pass

    async def _place_order_bets(self):
        depth_ratio, end = TRADES_DEPTH_THRESHOLDS
        step = TRADES_DEPTH_RATIO_STEP
        while depth_ratio < end:
            self._trader.tick_place_order(depth_ratio, self._best_bid_price, self._best_ask_price)
            depth_ratio += step
        pass

    async def _handle_ticker_ws(self, ticker_stream: ReconnectingWebsocket) -> None:
        """WebSocket ticker stream callback
        https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-book-ticker-streams
        Individual Symbol Book Ticker Streams
        Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.
        Stream Name: <symbol>@bookTicker
        Update Speed: Real-time
        """
        async with ticker_stream as stream:
            while True:
                res = await stream.recv()
                logging.debug(f'TICKER/JSON {res!r}')
                await self.handle_ticker_payload(res)

    async def _handle_trades_ws(self, trades_stream: ReconnectingWebsocket) -> None:
        """ WebSocket trades stream callback
        https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#trade-streams
        The Trade Streams push raw trade information; each trade has a unique buyer and seller.
        Stream Name: <symbol>@trade
        Update Speed: Real-time
        """
        async with trades_stream as stream:
            while True:
                res = await stream.recv()
                logging.debug(f'TRADE/JSON {res!r}')
                await self.handle_trades_payload(res)

    async def _timer_handler(self):
        await self.handle_timer_tick()

    async def _report_handler(self):
        bid, ask = await self.report_bet_for_threshlod(REPORT_MAIN_BET_THRESHOLD)
        logging.error(f'BET bid={bid} ask={ask} / best_bid={self._best_bid_price} best_ask={self._best_ask_price}')
        pass

    async def run(self) -> None:
        logging.info('Binance API Key: %s...%s' % (self._binance_api_key[:3], self._binance_api_key[-3:]))
        logging.info(f'Symbol pair: {self.pair()}')
        binance_api_client = await AsyncClient.create(
            api_key=self._binance_api_key,
            api_secret=self._binance_api_secret,
        )
        binance_ws = BinanceSocketManager(binance_api_client)

        symbol_ticker_socket = binance_ws.symbol_book_ticker_socket(self.pair())
        trade_socket = binance_ws.trade_socket(self.pair())
        montecarlo_trader_timer = Timer(TRADES_BETS_FREQUENCY_SECONDS, self._timer_handler)
        report_timer = Timer(REPORT_MAIN_BET_FREQUENCY_SECONDS, self._report_handler)

        try:
            await asyncio.gather(
                self._handle_ticker_ws(symbol_ticker_socket),
                self._handle_trades_ws(trade_socket),
                montecarlo_trader_timer.start(),
                report_timer.start(),
            )
        finally:
            # TODO: infinite loop above, does not happen, program kills on ^C KeyboardInterrupt
            # Safer way to additionally setup SIGNAL handlers
            await binance_api_client.close_connection()
            await montecarlo_trader_timer.cancel()
