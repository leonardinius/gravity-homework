from __future__ import annotations

import time
from typing import TypeVar, Generic

T = TypeVar('T')


class SlidingWindow(Generic[T]):
    _seconds: float
    _list = list[tuple[float, T]]

    def __init__(self, seconds: float, time_function=time.time) -> None:
        self._seconds = abs(seconds)
        self._list = list()
        self._time = time_function

    def put(self, timestamp: float, value: T) -> SlidingWindow[T]:
        if self._matches(timestamp):
            self._list.append((timestamp, value))

        # Premature? optimization: to amortize the removal of out of time window elements
        self._pack0()
        return self

    def pack(self) -> list[tuple[float, T]]:
        # TODO: review, it likely can be performance issue here
        self._list = sorted(self._list, key=lambda item: item[0])
        self._pack0()
        return self._list

    def _pack0(self) -> SlidingWindow[T]:
        while len(self._list) > 0 and not self._matches(self._list[0][0]):
            self._list.pop(0)
        while len(self._list) > 0 and not self._matches(self._list[-1:][0][0]):
            self._list.pop()
        return self

    def _matches(self, occurred_at: float) -> bool:
        return self._time() - occurred_at <= self._seconds

    def len(self):
        return len(self._list)
