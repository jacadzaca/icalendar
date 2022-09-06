'''Issue #82 - vBinary __repr__ called rather than to_ical from
               container types
see https://github.com/collective/icalendar/issues/82
'''

from icalendar import vBinary, Event

# is that what the test does?
def test_issue_82_encodes_vBinary_base64():
    b = vBinary('text')
    b.params['FMTTYPE'] = 'text/plain'
    assert b.to_ical() == b'dGV4dA=='

def test_issue_82_encodes_attach_base64():
    b = vBinary('text')
    b.params['FMTTYPE'] = 'text/plain'
    event = Event()
    event.add('ATTACH', b)
    assert event.to_ical() == b'BEGIN:VEVENT\r\nATTACH;ENCODING=BASE64;FMTTYPE=text/plain;VALUE=BINARY:dGV4dA==\r\nEND:VEVENT\r\n'

