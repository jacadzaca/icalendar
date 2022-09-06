'''Issue #112 - No timezone info on EXDATE
https://github.com/collective/icalendar/issues/112
'''
import pytest

from icalendar.parser_tools import to_unicode

@pytest.mark.parametrize('timezone_info', [
    # General timezone aware dates in ical string
    ('DTSTART;TZID=America/New_York:20130907T120000'),
    ('DTEND;TZID=America/New_York:20130907T170000'),
    # Specific timezone aware exdates in ical string
    ('EXDATE;TZID=America/New_York:20131012T120000'),
    ('EXDATE;TZID=America/New_York:20131011T120000')
])
def test_issue_112_timezone_info_present_in_ical(events, timezone_info):
    timezone_info in events.issue_112_missing_tzinfo_on_exdate.to_ical().decode('utf-8')

def test_issue_112_timezone_name_parsed(events):
    assert events.issue_112_missing_tzinfo_on_exdate['exdate'][0].dts[0].dt.tzname() == 'EDT'
