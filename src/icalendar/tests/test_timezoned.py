import unittest

import datetime
import dateutil.parser
import icalendar
from icalendar import Calendar, Timezone, TimezoneStandard, TimezoneDaylight, Event
import os
import pytz
try:
    import zoneinfo
except:
    from backports import zoneinfo

def test_from_ical_decodes_timezones(calendars, in_timezone):
    assert calendars.timezoned['PRODID'] == '-//Plone.org//NONSGML plone.app.event//EN'
    timezones = calendars.timezoned.walk('VTIMEZONE')
    assert len(timezones) == 1
    assert timezones[0]['tzid'].to_ical() == b'Europe/Vienna'
    assert timezones[0].walk('STANDARD')[0].decoded('TZOFFSETFROM') == datetime.timedelta(0, 7200)
    event = calendars.timezoned.walk('VEVENT')[0]
    assert event.decoded('DTSTART') == in_timezone(datetime.datetime(2012, 2, 13, 10, 0, 0), 'Europe/Vienna')
    assert event.decoded('DTSTAMP') == in_timezone(datetime.datetime(2010, 10, 10, 9, 10, 10), 'UTC')

def test_to_ical_encodes_timezones(calendars, in_timezone):
    cal = Calendar()
    cal.add('prodid', "-//Plone.org//NONSGML plone.app.event//EN")
    cal.add('version', "2.0")
    cal.add('x-wr-calname', "test create calendar")
    cal.add('x-wr-caldesc', "icalendar tests")
    cal.add('x-wr-relcalid', "12345")
    cal.add('x-wr-timezone', "Europe/Vienna")

    tzc = Timezone()
    tzc.add('tzid', 'Europe/Vienna')
    tzc.add('x-lic-location', 'Europe/Vienna')

    tzs = TimezoneStandard()
    tzs.add('tzname', 'CET')
    tzs.add('dtstart', datetime.datetime(1970, 10, 25, 3, 0, 0))
    tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
    tzs.add('TZOFFSETFROM', datetime.timedelta(hours=2))
    tzs.add('TZOFFSETTO', datetime.timedelta(hours=1))

    tzd = TimezoneDaylight()
    tzd.add('tzname', 'CEST')
    tzd.add('dtstart', datetime.datetime(1970, 3, 29, 2, 0, 0))
    tzs.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
    tzd.add('TZOFFSETFROM', datetime.timedelta(hours=1))
    tzd.add('TZOFFSETTO', datetime.timedelta(hours=2))

    tzc.add_component(tzs)
    tzc.add_component(tzd)
    cal.add_component(tzc)

    event = icalendar.Event()
    event.add(
        'dtstart',
        in_timezone(datetime.datetime(2012, 2, 13, 10, 00, 00), 'Europe/Vienna'))
    event.add(
        'dtend',
        in_timezone(datetime.datetime(2012, 2, 17, 18, 00, 00), 'Europe/Vienna'))
    event.add(
        'dtstamp',
        in_timezone(datetime.datetime(2010, 10, 10, 10, 10, 10), 'Europe/Vienna'))
    event.add(
        'created',
        in_timezone(datetime.datetime(2010, 10, 10, 10, 10, 10), 'Europe/Vienna'))
    event.add('uid', '123456')
    event.add(
        'last-modified',
        in_timezone(datetime.datetime(2010, 10, 10, 10, 10, 10), 'Europe/Vienna'))
    event.add('summary', 'artsprint 2012')
    event.add('description', 'sprinting at the artsprint')
    event.add('location', 'aka bild, wien')
    event.add('categories', 'first subject')
    event.add('categories', 'second subject')
    event.add('attendee', 'häns')
    event.add('attendee', 'franz')
    event.add('attendee', 'sepp')
    event.add('contact', 'Max Mustermann, 1010 Wien')
    event.add('url', 'https://plone.org')
    cal.add_component(event)
    cal.to_ical().decode('utf-8') == calendars.timezone_encoding.raw_ics

class TestTimezoned(unittest.TestCase):
    def test_tzinfo_dateutil(self):
        # Test for issues #77, #63
        # references: #73,7430b66862346fe3a6a100ab25e35a8711446717
        date = dateutil.parser.parse('2012-08-30T22:41:00Z')
        date2 = dateutil.parser.parse('2012-08-30T22:41:00 +02:00')
        self.assertTrue(date.tzinfo.__module__.startswith('dateutil.tz'))
        self.assertTrue(date2.tzinfo.__module__.startswith('dateutil.tz'))

        # make sure, it's parsed properly and doesn't throw an error
        self.assertTrue(icalendar.vDDDTypes(date).to_ical()
                        == b'20120830T224100Z')
        self.assertTrue(icalendar.vDDDTypes(date2).to_ical()
                        == b'20120830T224100')


class TestTimezoneCreation(unittest.TestCase):

    def test_create_america_new_york(self):
        """testing America/New_York, the most complex example from the
        RFC"""

        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'america_new_york.ics'), 'rb') as fp:
            data = fp.read()
        cal = icalendar.Calendar.from_ical(data)

        tz = cal.walk('VEVENT')[0]['DTSTART'][0].dt.tzinfo
        self.assertEqual(str(tz), 'custom_America/New_York')
        pytz_new_york = pytz.timezone('America/New_York')
        # for reasons (tm) the locally installed version of the time zone
        # database isn't always complete, therefore we only compare some
        # transition times
        ny_transition_times = []
        ny_transition_info = []
        for num, date in enumerate(pytz_new_york._utc_transition_times):
            if datetime.datetime(1967, 4, 30, 7, 0)\
                    <= date <= datetime.datetime(2037, 11, 1, 6, 0):
                ny_transition_times.append(date)
                ny_transition_info.append(pytz_new_york._transition_info[num])
        self.assertEqual(tz._utc_transition_times[:142], ny_transition_times)
        self.assertEqual(tz._transition_info[0:142], ny_transition_info)
        self.assertIn(
            (
                datetime.timedelta(-1, 72000),
                datetime.timedelta(0, 3600), 'EDT'
            ),
            tz._tzinfos.keys()
        )
        self.assertIn(
            (datetime.timedelta(-1, 68400), datetime.timedelta(0), 'EST'),
            tz._tzinfos.keys()
        )

    def test_create_pacific_fiji(self):
        """testing Pacific/Fiji, another pretty complex example with more than
        one RDATE property per subcomponent"""
        self.maxDiff = None

        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'pacific_fiji.ics'), 'rb') as fp:
            data = fp.read()
        cal = icalendar.Calendar.from_ical(data)

        tz = cal.walk('VEVENT')[0]['DTSTART'][0].dt.tzinfo
        self.assertEqual(str(tz), 'custom_Pacific/Fiji')
        self.assertEqual(tz._utc_transition_times,
                         [datetime.datetime(1915, 10, 25, 12, 4),
                          datetime.datetime(1998, 10, 31, 14, 0),
                          datetime.datetime(1999, 2, 27, 14, 0),
                          datetime.datetime(1999, 11, 6, 14, 0),
                          datetime.datetime(2000, 2, 26, 14, 0),
                          datetime.datetime(2009, 11, 28, 14, 0),
                          datetime.datetime(2010, 3, 27, 14, 0),
                          datetime.datetime(2010, 10, 23, 14, 0),
                          datetime.datetime(2011, 3, 5, 14, 0),
                          datetime.datetime(2011, 10, 22, 14, 0),
                          datetime.datetime(2012, 1, 21, 14, 0),
                          datetime.datetime(2012, 10, 20, 14, 0),
                          datetime.datetime(2013, 1, 19, 14, 0),
                          datetime.datetime(2013, 10, 26, 14, 0),
                          datetime.datetime(2014, 1, 18, 13, 0),
                          datetime.datetime(2014, 10, 25, 14, 0),
                          datetime.datetime(2015, 1, 17, 13, 0),
                          datetime.datetime(2015, 10, 24, 14, 0),
                          datetime.datetime(2016, 1, 23, 13, 0),
                          datetime.datetime(2016, 10, 22, 14, 0),
                          datetime.datetime(2017, 1, 21, 13, 0),
                          datetime.datetime(2017, 10, 21, 14, 0),
                          datetime.datetime(2018, 1, 20, 13, 0),
                          datetime.datetime(2018, 10, 20, 14, 0),
                          datetime.datetime(2019, 1, 19, 13, 0),
                          datetime.datetime(2019, 10, 26, 14, 0),
                          datetime.datetime(2020, 1, 18, 13, 0),
                          datetime.datetime(2020, 10, 24, 14, 0),
                          datetime.datetime(2021, 1, 23, 13, 0),
                          datetime.datetime(2021, 10, 23, 14, 0),
                          datetime.datetime(2022, 1, 22, 13, 0),
                          datetime.datetime(2022, 10, 22, 14, 0),
                          datetime.datetime(2023, 1, 21, 13, 0),
                          datetime.datetime(2023, 10, 21, 14, 0),
                          datetime.datetime(2024, 1, 20, 13, 0),
                          datetime.datetime(2024, 10, 26, 14, 0),
                          datetime.datetime(2025, 1, 18, 13, 0),
                          datetime.datetime(2025, 10, 25, 14, 0),
                          datetime.datetime(2026, 1, 17, 13, 0),
                          datetime.datetime(2026, 10, 24, 14, 0),
                          datetime.datetime(2027, 1, 23, 13, 0),
                          datetime.datetime(2027, 10, 23, 14, 0),
                          datetime.datetime(2028, 1, 22, 13, 0),
                          datetime.datetime(2028, 10, 21, 14, 0),
                          datetime.datetime(2029, 1, 20, 13, 0),
                          datetime.datetime(2029, 10, 20, 14, 0),
                          datetime.datetime(2030, 1, 19, 13, 0),
                          datetime.datetime(2030, 10, 26, 14, 0),
                          datetime.datetime(2031, 1, 18, 13, 0),
                          datetime.datetime(2031, 10, 25, 14, 0),
                          datetime.datetime(2032, 1, 17, 13, 0),
                          datetime.datetime(2032, 10, 23, 14, 0),
                          datetime.datetime(2033, 1, 22, 13, 0),
                          datetime.datetime(2033, 10, 22, 14, 0),
                          datetime.datetime(2034, 1, 21, 13, 0),
                          datetime.datetime(2034, 10, 21, 14, 0),
                          datetime.datetime(2035, 1, 20, 13, 0),
                          datetime.datetime(2035, 10, 20, 14, 0),
                          datetime.datetime(2036, 1, 19, 13, 0),
                          datetime.datetime(2036, 10, 25, 14, 0),
                          datetime.datetime(2037, 1, 17, 13, 0),
                          datetime.datetime(2037, 10, 24, 14, 0),
                          datetime.datetime(2038, 1, 23, 13, 0),
                          datetime.datetime(2038, 10, 23, 14, 0)]

                         )
        self.assertEqual(
            tz._transition_info,
            [(
                datetime.timedelta(0, 43200),
                datetime.timedelta(0),
                'custom_Pacific/Fiji_19151026T000000_+115544_+1200'
            )] +
            3 * [(
                datetime.timedelta(0, 46800),
                datetime.timedelta(0, 3600),
                'custom_Pacific/Fiji_19981101T020000_+1200_+1300'
            ), (
                datetime.timedelta(0, 43200),
                datetime.timedelta(0),
                'custom_Pacific/Fiji_19990228T030000_+1300_+1200')
            ] +
            3 * [(
                datetime.timedelta(0, 46800),
                datetime.timedelta(0, 3600),
                'custom_Pacific/Fiji_20101024T020000_+1200_+1300'
            ), (
                datetime.timedelta(0, 43200),
                datetime.timedelta(0),
                'custom_Pacific/Fiji_19990228T030000_+1300_+1200'
            )] +
            25 * [(
                datetime.timedelta(0, 46800),
                datetime.timedelta(0, 3600),
                'custom_Pacific/Fiji_20101024T020000_+1200_+1300'
            ), (
                datetime.timedelta(0, 43200),
                datetime.timedelta(0),
                'custom_Pacific/Fiji_20140119T020000_+1300_+1200'
            )] +
            [(
                datetime.timedelta(0, 46800),
                datetime.timedelta(0, 3600),
                'custom_Pacific/Fiji_20101024T020000_+1200_+1300'
            )]
        )

        self.assertIn(
            (
                datetime.timedelta(0, 46800),
                datetime.timedelta(0, 3600),
                'custom_Pacific/Fiji_19981101T020000_+1200_+1300'
            ),
            tz._tzinfos.keys()
        )
        self.assertIn(
            (
                datetime.timedelta(0, 43200),
                datetime.timedelta(0),
                'custom_Pacific/Fiji_19990228T030000_+1300_+1200'
            ),
            tz._tzinfos.keys()
        )

    def test_same_start_date(self):
        """testing if we can handle VTIMEZONEs whose different components
        have the same start DTIMEs."""
        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'timezone_same_start.ics'), 'rb') as fp:
            data = fp.read()
        cal = icalendar.Calendar.from_ical(data)
        d = cal.subcomponents[1]['DTSTART'].dt
        self.assertEqual(d.strftime('%c'), 'Fri Feb 24 12:00:00 2017')

    def test_same_start_date_and_offset(self):
        """testing if we can handle VTIMEZONEs whose different components
        have the same DTSTARTs, TZOFFSETFROM, and TZOFFSETTO."""
        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'timezone_same_start_and_offset.ics'), 'rb') as fp:
            data = fp.read()
        cal = icalendar.Calendar.from_ical(data)
        d = cal.subcomponents[1]['DTSTART'].dt
        self.assertEqual(d.strftime('%c'), 'Fri Feb 24 12:00:00 2017')

    def test_rdate(self):
        """testing if we can handle VTIMEZONEs who only have an RDATE, not RRULE
        """
        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'timezone_rdate.ics'), 'rb') as fp:
            data = fp.read()
        cal = icalendar.Calendar.from_ical(data)
        vevent = cal.walk('VEVENT')[0]
        tz = vevent['DTSTART'].dt.tzinfo
        self.assertEqual(str(tz), 'posix/Europe/Vaduz')
        self.assertEqual(
            tz._utc_transition_times[:6],
            [
                datetime.datetime(1901, 12, 13, 20, 45, 38),
                datetime.datetime(1941, 5, 5, 0, 0, 0),
                datetime.datetime(1941, 10, 6, 0, 0, 0),
                datetime.datetime(1942, 5, 4, 0, 0, 0),
                datetime.datetime(1942, 10, 5, 0, 0, 0),
                datetime.datetime(1981, 3, 29, 1, 0),
            ])
        self.assertEqual(
            tz._transition_info[:6],
            [
                (datetime.timedelta(0, 3600), datetime.timedelta(0), 'CET'),
                (datetime.timedelta(0, 7200), datetime.timedelta(0, 3600), 'CEST'),
                (datetime.timedelta(0, 3600), datetime.timedelta(0), 'CET'),
                (datetime.timedelta(0, 7200), datetime.timedelta(0, 3600), 'CEST'),
                (datetime.timedelta(0, 3600), datetime.timedelta(0), 'CET'),
                (datetime.timedelta(0, 7200), datetime.timedelta(0, 3600), 'CEST'),
            ]
        )
