"""Conversion utilities"""
from datetime import datetime, timezone, timedelta

from pytimeparse.timeparse import timeparse

from skytracker.utils import log_and_raise


def time_string_to_seconds(time_string: str) -> int:
    """Convert a time string to number of seconds

    Args:
        time_string (str): time string (i.e. "1d5h", "2h30m", or "5m20s")

    Returns:
        int: number of seconds the time string specified
    """
    seconds = timeparse(time_string)
    if seconds is None:
        log_and_raise(ValueError, f'Time string could not be parsed ({time_string})')
    return int(seconds)


def datetime_ago_from_time_string(time_string: str) -> datetime:
    """Get the date and time which is a specified amount of time ago

    Args:
        time_string (str): time string (i.e. "1d5h", "2h30m", or "5m20s")

    Returns:
        datetime: datetime which is specified amount of time ago
    """
    now = datetime.now(timezone.utc)
    seconds = time_string_to_seconds(time_string)
    return now - timedelta(seconds=seconds)
