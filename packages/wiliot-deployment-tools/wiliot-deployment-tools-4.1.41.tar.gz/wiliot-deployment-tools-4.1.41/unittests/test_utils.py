import unittest
try:
    from zoneinfo import ZoneInfo  # will run only in python 3.9+
except ImportError:
    from backports.zoneinfo import ZoneInfo  # backport to python < 3.9
from wiliot_deployment_tools.common.utils import *

class UtilsTest(unittest.TestCase):

    def test_convert_datetime_to_timestamp(self):
        now = datetime.datetime.now()
        timestamp = now.timestamp()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        micro = now.microsecond
        self.assertEquals(convert_datetime_to_timestamp(year, month, day, hour, minute, second, micro, hours_from_utc=2), math.ceil(timestamp * 1000))

    def test_ms_timestamp_to_timezone(self):
        now = datetime.datetime.now()
        ms_timestamp = now.timestamp()*1000
        tzs = ['Israel', 'America/Los_Angeles', 'Europe/Vienna']
        for tz in tzs:
            timezone = ZoneInfo(tz)
            # hour = true, milli = true
            strftime = now.astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S.%f %Z')
            self.assertEquals(mstimestamp_to_timezone(ms_timestamp, tz, milli=True, hour=True), strftime)
            # hour = true, milli = false
            strftime = now.astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S %Z')
            self.assertEquals(mstimestamp_to_timezone(ms_timestamp, tz, milli=False, hour=True), strftime)
            # hour = false
            strftime = now.astimezone(timezone).strftime('%Y-%m-%d')
            self.assertEquals(mstimestamp_to_timezone(ms_timestamp, tz, hour=False), strftime)

    def test_convert_timestamp_to_datetime(self):
        now = datetime.datetime.now()
        timestamp = now.timestamp()
        ms_timestamp = timestamp*1000
        self.assertEquals(now, convert_timestamp_to_datetime(ms_timestamp))
        self.assertEquals(now, convert_timestamp_to_datetime(timestamp))
    
    def test_datetime_to_timezone(self):
        now = datetime.datetime.now()
        tzs = ['Israel', 'America/Los_Angeles', 'Europe/Vienna']
        for tz in tzs:
            self.assertEquals(now.astimezone(ZoneInfo(tz)), datetime_to_timezone(now, tz))

if __name__ == '__main__':
    unittest.main()
