from __future__ import annotations

from datetime import timedelta

from pytimeparse import parse


class Duration(timedelta):
    """
    A subclass of timedelta that adds some useful methods for converting the duration to other units.
    Added methods:
    - total_milliseconds
    - total_minutes
    - total_hours
    - total_days

    It also provides a static constructor to parse a time string and return a Duration object. For more details,
    refer to parse_str method.
    """

    def total_milliseconds(self) -> float:
        return self / timedelta(milliseconds=1)

    def total_minutes(self) -> float:
        return self / timedelta(minutes=1)

    def total_hours(self) -> float:
        return self / timedelta(hours=1)

    def total_days(self) -> float:
        return self / timedelta(days=1)

    @classmethod
    def parse_str(cls, time_str: str) -> Duration:
        """
        Parse a time string and return a Duration object. The supported format are listed here:
        https://github.com/wroberts/pytimeparse

        :raises ValueError: If the time string is invalid. Refer to the link above for the supported format.
        """
        seconds = parse(time_str)

        if seconds is None:
            raise ValueError(f'Invalid time string: {time_str}')

        return cls(seconds=seconds)
