''' Issue #104 - line parsing error in a VEVENT
(which has ignore_exceptions). Should mark the event broken
but not raise an exception.

see https://github.com/collective/icalendar/issues/104
'''

from icalendar import Event

def test_issue_104__ignore_exceptions(events):
    assert events.issue_104_mark_events_broken.is_broken # TODO: REMOVE FOR NEXT MAJOR RELEASE
    assert events.issue_104_mark_events_broken.errors == [(None, "Content line could not be parsed into parts: 'X': Invalid content line")]

