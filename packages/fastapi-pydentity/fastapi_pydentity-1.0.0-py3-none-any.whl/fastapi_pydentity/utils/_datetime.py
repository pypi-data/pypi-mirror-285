from datetime import datetime as __datetime, timedelta, UTC
from typing import Self


class datetime(__datetime):
    @classmethod
    def utcnow(cls) -> Self:
        return datetime.now(UTC)

    def add(self, _timedelta: timedelta, /) -> Self:
        return self.__add__(_timedelta)

    def add_days(self, days: float, /) -> Self:
        return self.add(timedelta(days=days))

    def add_seconds(self, seconds: float, /) -> Self:
        return self.add(timedelta(seconds=seconds))

    def add_microseconds(self, microseconds: float, /) -> Self:
        return self.add(timedelta(microseconds=microseconds))

    def add_milliseconds(self, milliseconds: float, /) -> Self:
        return self.add(timedelta(milliseconds=milliseconds))

    def add_minutes(self, minutes: float, /) -> Self:
        return self.add(timedelta(minutes=minutes))

    def add_hours(self, hours: float, /) -> Self:
        return self.add(timedelta(hours=hours))

    def add_weeks(self, weeks: float, /) -> Self:
        return self.add(timedelta(weeks=weeks))
