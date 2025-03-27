"""Functions for handling datetime types.

Parsing dates from strings, setting timezones or converting
datatime objects are complex and prone error tasks. This module
offers a toolkit to make easier to deal with those problems.
"""

import datetime
import logging
import re

import dateutil.parser
import dateutil.rrule
import dateutil.tz
from dateutil.relativedelta import relativedelta

import pandas as pd

__all__ = [
    "InvalidDateError", "datetime_utcnow", "datetime_to_utc",
    "str_to_datetime", "unixtime_to_datetime"
]

logger = logging.getLogger(__name__)


class InvalidDateError(Exception):
    """Exception raised when a date is invalid"""

    message = "%(date)s is not a valid date"

    def __init__(self, **kwargs):
        super().__init__()
        self.msg = self.message % kwargs

    def __str__(self):
        return self.msg


def datetime_utcnow():
    """Handy function which returns the current date and time in UTC."""

    return datetime.datetime.now(datetime.timezone.utc)


def datetime_to_utc(ts):
    """Convert a timestamp to UTC+0 timezone.

    Returns the given datetime object converted to a date with
    UTC+0 timezone. For naive datetimes, it will be assumed that
    they are in UTC+0. When the timezone is wrong, UTC+0 will
    be set as default (using `dateutil.tz.tzutc` object).

    :param dt: timestamp to convert

    :returns: a datetime object

    :raises InvalidDateError: when the given parameter is not an
        instance of datetime
    """
    if not isinstance(ts, datetime.datetime):
        msg = '<%s> object' % type(ts)
        raise InvalidDateError(date=msg)

    if not ts.tzinfo:
        ts = ts.replace(tzinfo=dateutil.tz.tzutc())

    try:
        ts = ts.astimezone(dateutil.tz.tzutc())
    except ValueError:
        logger.warning("Date %s str does not have a valid timezone", ts)
        logger.warning("Date converted to UTC removing timezone info")
        ts = ts.replace(tzinfo=dateutil.tz.tzutc()).astimezone(dateutil.tz.tzutc())

    return ts


def str_to_datetime(ts):
    """Format a string to a datetime object.

    This functions supports several date formats like YYYY-MM-DD,
    MM-DD-YYYY, YY-MM-DD, YYYY-MM-DD HH:mm:SS +HH:MM, among others.
    When the timezone is not provided, UTC+0 will be set as default
    (using `dateutil.tz.tzutc` object).

    :param ts: string to convert

    :returns: a datetime object

    :raises IvalidDateError: when the given string cannot be converted
        on a valid date
    """

    def parse_datetime(ts):
        dt = dateutil.parser.parse(ts)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=dateutil.tz.tzutc())
        return dt

    if not ts:
        raise InvalidDateError(date=str(ts))

    try:
        # Try to remove additional information after
        # timezone section because it cannot be parsed,
        # like in 'Wed, 26 Oct 2005 15:20:32 -0100 (GMT+1)'
        # or in 'Thu, 14 Aug 2008 02:07:59 +0200 CEST'.
        m = re.search(r"^.+?\s+[\+\-\d]\d{4}(\s+.+)$", ts)
        if m:
            ts = ts[:m.start(1)]

        try:
            dt = parse_datetime(ts)
        except ValueError as e:
            # Try to remove the timezone, usually it causes
            # problems.
            m = re.search(r"^(.+?)\s+[\+\-\d]\d{4}.*$", ts)

            if m:
                dt = parse_datetime(m.group(1))
                logger.warning("Date %s does not have a valid timezone. "
                               "Date converted removing timezone info", ts)
                return dt

            raise e

        try:
            # Check that the offset is between -timedelta(hours=24) and
            # timedelta(hours=24). If it is not the case, convert the
            # date to UTC and remove the timezone info.
            _ = dt.astimezone(dateutil.tz.tzutc())
        except ValueError:
            logger.warning("Date %s does not have a valid timezone; timedelta not in range. "
                           "Date converted to UTC removing timezone info", ts)
            dt = dt.replace(tzinfo=dateutil.tz.tzutc()).astimezone(dateutil.tz.tzutc())

        return dt

    except ValueError as e:
        raise InvalidDateError(date=str(ts))


def unixtime_to_datetime(ut):
    """Convert a unixtime timestamp to a datetime object.

    The function converts a timestamp in Unix format to a
    datetime object. UTC timezone will also be set.

    :param ut: Unix timestamp to convert

    :returns: a datetime object

    :raises InvalidDateError: when the given timestamp cannot be
        converted into a valid date
    """
    try:
        dt = datetime.datetime.utcfromtimestamp(ut)
        dt = dt.replace(tzinfo=dateutil.tz.tzutc())
        return dt
    except Exception:
        raise InvalidDateError(date=str(ut))


def get_time_diff_months(start, end):
    """ Number of months between two dates in UTC format  """
    return get_time_diff_date(start, end, "month")


def get_time_diff_days(start, end):
    ''' Number of days between two dates in UTC format  '''
    return get_time_diff_date(start, end, "day")

def get_time_diff_date(start, end, date_type="day"):
    ''' Number of date between two dates in UTC format  '''

    if start is None or end is None:
        return None

    if type(start) is not datetime.datetime:
        start = parse(start)
    if type(end) is not datetime.datetime:
        end = parse(end)

    if date_type == "minute":
        seconds_date = float(60)
    elif date_type == "hour":
        seconds_date = float(60 * 60)
    elif date_type == "day":
        seconds_date = float(60 * 60 * 24)
    elif date_type == "month":
        seconds_date = float(60 * 60 * 24 * 30)
    
    diff_date = (end - start).total_seconds() / seconds_date
    diff_date = float('%.2f' % diff_date)

    return diff_date


def check_times_has_overlap(start_time1, end_time1, start_time2, end_time2):
    """ Check for overlap between the two time ranges """
    return not (end_time1 < start_time2 or start_time1 > end_time2)


def get_oldest_date(date1, date2):
    """ Two times to get the oldest time """
    return date2 if date1 >= date2 else date1


def get_latest_date(date1, date2):
    """ Two times to get the latest time """
    return date1 if date1 >= date2 else date2

def get_date_list(begin_date, end_date, freq='W-MON'):
    '''Get date list from begin_date to end_date every Monday'''
    date_list = [x for x in list(pd.date_range(freq=freq, start=datetime_to_utc(
        str_to_datetime(begin_date)), end=datetime_to_utc(str_to_datetime(end_date))))]
    return date_list

def parse(date_str):
    try:
        time_format = "%Y-%m-%dT%H:%M:%S"
        date = datetime.datetime.strptime(date_str[:19], time_format)
    except Exception:
        date = str_to_datetime(date_str).replace(tzinfo=None)
    return date
def get_last_three_years_dates():
    '''Get January 1st of the last three years including the current year'''
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    dates = [datetime.datetime(year, 12, 31) for year in range(current_year - 2, current_year)]
    current_month_first = datetime.datetime(current_year, current_month, 1)
    dates.append(current_month_first)
    return dates

def get_last_four_quarters_dates():
    '''获取最近四个季度的最后一天，包括当前季度'''
    current_date = datetime.datetime.now()
    quarter_end_dates = []
    current_month = current_date.month
    if current_month in [1, 2, 3]:
        current_quarter_end = datetime.datetime(current_date.year, 3, 31)
    elif current_month in [4, 5, 6]:
        current_quarter_end = datetime.datetime(current_date.year, 6, 30)
    elif current_month in [7, 8, 9]:
        current_quarter_end = datetime.datetime(current_date.year, 9, 30)
    else:
        current_quarter_end = datetime.datetime(current_date.year, 12, 31)
    quarter_end_dates.append(current_quarter_end)

    # 添加之前三个季度的最后一天
    for _ in range(3):
        current_quarter_end -= relativedelta(months=3)
        quarter_end_dates.append(current_quarter_end)

    return quarter_end_dates

