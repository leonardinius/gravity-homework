import datetime
import time
from unittest import mock
from homework import timewindow


def delorean_time():
    back_to_future_datetime = datetime.datetime.fromisoformat('2015-10-21')
    return back_to_future_datetime.timestamp()


def test_sliding_window_time_range():
    # we are interested in last 5 minutes
    window = timewindow.SlidingWindow[str](300, delorean_time)

    window.put(delorean_time() - 500, '1')  # too old
    window.put(delorean_time() - 301, '2')  # 1 sec to late
    window.put(delorean_time() - 300, '3')  # ok
    window.put(delorean_time() - 299, '4')  # ok

    assert window.pack() == [
        (delorean_time() - 300, '3'),
        (delorean_time() - 299, '4')
    ]


def test_sliding_window_removes_elements():
    # we are interested in last 5 seconds
    window = timewindow.SlidingWindow[str](5)
    # tick, system time is set to 10
    window._time = lambda: 10

    window.put(1, '1')
    window.put(10, '10')

    # tick, system time is set to 15
    window.put(11, '11')
    window.put(15, '15')

    assert window.pack() == [
        (10, '10'),
        (11, '11'),
        (15, '15'),
    ]
