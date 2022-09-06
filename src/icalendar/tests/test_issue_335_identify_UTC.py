'''Why is tools.UIDGenerator a class (that must be instantiated) instead of a module? #345

see https://github.com/collective/icalendar/issues/345
'''

import pytz
import pytest
from dateutil import tz
from datetime import datetime

try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo

from icalendar import Event

@pytest.mark.parametrize('zone', [
    pytz.utc,
    zoneinfo.ZoneInfo('UTC'),
    pytz.timezone('UTC'),
    tz.UTC,
    tz.gettz('UTC')])
def test_issue_335_identify_UTC(zone):
    myevent = Event()
    dt = datetime(2021, 11, 17, 15, 9, 15)
    myevent.add('dtstart', dt.astimezone(zone))
    assert 'DTSTART;VALUE=DATE-TIME:20211117T150915Z' in myevent.to_ical().decode('ASCII')
