import datetime

from homework import timewindow


def _delorean_time():
    back_to_future_datetime = datetime.datetime.fromisoformat('2015-10-21')
    return back_to_future_datetime.timestamp()


def test_sliding_window_time_range():
    # we are interested in last 5 minutes
    window = timewindow.SlidingWindow[str](300, _delorean_time)

    window.put(_delorean_time() - 500, '1')  # too old
    window.put(_delorean_time() - 301, '2')  # 1 sec to late
    window.put(_delorean_time() - 300, '3')  # ok
    window.put(_delorean_time() - 299, '4')  # ok

    assert window.pack() == [
        (_delorean_time() - 300, '3'),
        (_delorean_time() - 299, '4')
    ]


def test_sliding_window_removes_elements():
    # we are interested in last 5 seconds
    window = timewindow.SlidingWindow[str](5)
    # tick, system time is set to 10
    window._time = lambda: 10.0

    window.put(1.0, '1')
    window.put(10.0, '10')

    # tick, system time is set to 15
    window.put(11.0, '11')
    window.put(15.0, '15')

    assert window.pack() == [
        (10.0, '10'),
        (11.0, '11'),
        (15.0, '15'),
    ]
