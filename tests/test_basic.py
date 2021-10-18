import datetime
import time
from unittest import mock

back_to_future_datetime = datetime.datetime.fromisoformat('2015-10-21')


@mock.patch('time.time', mock.MagicMock(return_value=back_to_future_datetime.timestamp()))
def test_back_to_future_delorean_travel():
    assert datetime.datetime.fromtimestamp(time.time()).date().isoformat() == '2015-10-21'
