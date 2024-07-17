"""
Date and Time helper utilities
"""
from datetime import date, datetime, timezone
from typing import Optional


def get_current_epoch_time() -> int:
    """
    Gets currents epoch seconds

    Returns:
        int: current epoch time
    """
    return int(datetime.now().timestamp())


def epoch_to_datetime(epoch_time: int) -> datetime:
    """
    Converts Epoch time to Datetime format

    :param epoch_time: epoch seconds
    :type epoch_time: int
    :return: python datetime object
    :rtype: datetime
    """
    return datetime.utcfromtimestamp(epoch_time)


def date_to_epoch(input_date: date, timezone: timezone = timezone.utc) -> int:
    """
    Convert a date to the epoch equivalent

    :param input_date: Input Date
    :type input_date: date
    :param timezone: Timezone to convert to, defaults to timezone.utc
    :type timezone: timezone, optional
    :return: Epoch equivalent of the date
    :rtype: int
    """
    date_time = datetime(
        input_date.year, input_date.month, input_date.day, tzinfo=timezone
    )
    return int(date_time.timestamp())


def datetime_to_epoch(date_time: datetime) -> int:
    """
    Convert a datetime to epoch

    :param date_time: Datetime object
    :type date_time: datetime
    :return: Epoch equivalent
    :rtype: int
    """
    return int(date_time.timestamp())


def get_current_year() -> int:
    """
    Returns the current year

    :return: Current Year
    :rtype: int
    """
    return datetime.now().year


def string_to_datetime(
    str_dt: str,
    time_zone: Optional[timezone] = None,
    format: str = "%Y-%m-%dT%H:%M:%SZ",
) -> datetime:
    """
    Convert a string value to a datetime object

    :param str_dt: Datetime string
    :type str_dt: str
    :param time_zone: timezone to convert the string to
    :type time_zone: Optional[timezone]
    :param format: format to use when parsing, defaults to "YYYY-MM-DDTHH:MM:SSZ"
    :type format: str, optional
    :return: Datetime equivalent
    :rtype: datetime
    """
    if time_zone:
        date_time_obj = datetime.strptime(str_dt, format).replace(tzinfo=time_zone)

    else:
        date_time_obj = datetime.strptime(str_dt, format)

    return date_time_obj


def string_to_date(str_date: str, format: str = "%Y-%m-%d") -> date:
    """
    Converts a string value to a date

    :param str_date: String to convert
    :type str_date: str
    :param format: format to use when parsing, defaults to "%Y-%m-%d"
    :type format: str, optional
    :return: date object
    :rtype: date
    """
    return datetime.strptime(str_date, format).date()
