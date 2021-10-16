import asyncio
import time
from asyncio import Future


class Timer:
    _timeout: float
    _task: Future

    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback

    async def start(self):
        self._task = asyncio.ensure_future(self._tick())
        return self._task

    async def _tick(self):
        while not self._task.cancelled():
            time.sleep(self._timeout)
            await self._callback()

    def cancel(self):
        self._task.cancel()
