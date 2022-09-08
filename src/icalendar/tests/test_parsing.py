"""Tests checking that parsing/marshalling icals works"""
import pytest

from icalendar import Calendar, vRecur
from icalendar.parser import Contentline, Parameters

@pytest.mark.parametrize('raw_content_line, expected_output', [
    # Issue #142 - Multivalued parameters. This is needed for VCard 3.0.
    # see https://github.com/collective/icalendar/pull/142
    ('TEL;TYPE=HOME,VOICE:000000000', ('TEL', Parameters({'TYPE': ['HOME', 'VOICE']}), '000000000')),
    # Issue #143 - Allow dots in property names. Another vCard related issue.
    # see https://github.com/collective/icalendar/pull/143
    ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR:;;This is the Adress 08; Some City;;12345;Germany', ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR', Parameters(), ';;This is the Adress 08; Some City;;12345;Germany'))
])
def test_content_lines_parsed_properly(raw_content_line, expected_output):
    assert Contentline.from_ical(raw_content_line).parts() == expected_output

def test_issue_157_removes_trailing_semicolon(events):
    """Issue #157 - Recurring rules and trailing semicolons
    see https://github.com/collective/icalendar/pull/157"""
    recur = events.issue_157_removes_trailing_semicolon.decoded("RRULE")
    assert isinstance(recur, vRecur)
    assert recur.to_ical() == b'FREQ=YEARLY;BYDAY=1SU;BYMONTH=11'

@pytest.mark.parametrize('calendar_name', [
    # see https://github.com/collective/icalendar/issues/168
    ('keep_custom_properties'),

    # Issue #178 - A component with an unknown/invalid name is represented
    # as one of the known components, the information about the original
    # component name is lost.
    # see https://github.com/collective/icalendar/issues/178 https://github.com/collective/icalendar/pull/180
    # Parsing of a nonstandard component
    ('issue_178_component_with_invalid_name_represented'),
    # Nonstandard component inside other components, also has properties
    ('issue_178_custom_component_inside_other'),
    # Nonstandard component is able to contain other components
    ('issue_178_custom_component_contains_other')])
def test_calendar_to_ical_is_inverse_of_from_ical(calendars, calendar_name):
    calendar = getattr(calendars, calendar_name)
    assert calendar.to_ical() == calendar.raw_ics

@pytest.mark.parametrize('event_name', [
    ('issue_100_transformed_doctests_into_unittests'), # https://github.com/collective/icalendar/pull/100
    ('issue_184_broken_representation_of_period'),
])
def test_event_to_ical_is_inverse_of_from_ical(events, event_name):
    event = getattr(events, event_name)
    assert event.to_ical() == event.raw_ics

@pytest.mark.parametrize('timezone_file', [
    # Issue #55 - Parse error on utc-offset with seconds value
    # see https://github.com/collective/icalendar/issues/55
    'issue_55_parse_error_on_utc_offset_with_seconds',
])
def test_timezones_to_ical_is_inverse_of_from_ical(timezones, timezone_file):
    timezone = getattr(timezones, timezone_file)
    assert timezone.to_ical() == timezone.raw_ics

