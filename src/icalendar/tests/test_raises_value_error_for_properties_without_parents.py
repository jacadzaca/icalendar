'''Found an issue where from_ical() would raise ValueError for
properties without parent components.

see https://github.com/collective/icalendar/pull/179
'''

import pytest

from icalendar import Calendar

def test_raises_value_error_for_properties_without_parents():
    with pytest.raises(ValueError):
        Calendar.from_ical('VERSION:2.0')

