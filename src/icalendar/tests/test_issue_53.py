"""Issue #53 - Parsing failure on some descriptions?

see https://github.com/collective/icalendar/issues/53
"""

def test_issue_53_description_parsed_properly(events):
    event = events.issue_53_description_parsed_properly
    assert b'July 12 at 6:30 PM' in event.get('DESCRIPTION').to_ical()


def test_issue_53_tzid_parsed_properly(timezones):
    assert timezones.issue_53_tzid_parsed_properly['tzid'].to_ical() == b'America/New_York'

