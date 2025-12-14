from datetime import datetime, date


def datetimestring_to_datetime(*, datetimestring: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime | None:
    """
    Converts a datetime string to a datetime object.
    For formats see: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    """
    try:
        return datetime.strptime(datetimestring, format)
    except ValueError:
        return None


def calender_week(date: date) -> int:
    """
    Returns the calender week of a date.
    """
    return date.isocalendar().week
