'''Issue #58 - TZID on UTC DATE-TIMEs
see https://github.com/collective/icalendar/issues/58
'''

import pytest
import pytz
from datetime import datetime
from dateutil import tz
try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo

from icalendar import Event

@pytest.mark.parametrize('timezone', [
    pytz.utc,
    zoneinfo.ZoneInfo('UTC'),
    pytz.timezone('UTC'),
    tz.UTC,
    tz.gettz('UTC')])
def test_issue_58_no_tzid_when_utc(events, timezone):
    # According to RFC 2445: "The TZID property parameter MUST NOT be
    # applied to DATE-TIME or TIME properties whose time values are
    # specified in UTC.
    date = datetime(2012, 7, 16, 0, 0, 0)
    event = Event()
    event.add('dtstart', date.astimezone(timezone))
    assert event.to_ical() == events.issue_58_expected_output.raw_ics

