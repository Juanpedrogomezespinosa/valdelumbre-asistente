import re
from datetime import datetime, time

from app.domain.opening_query import OpeningQuery

_WEEKDAY_AND_TIME = re.compile(r"(?P<weekday>[1-7])T(?P<at>\d{2}:\d{2})")
_DATE_AND_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T.+")


def parse_open_at(value: str, now: datetime) -> OpeningQuery:
    """Read `abierto_en` (D-012): `1T12:00` or a full ISO date and time.

    `now` is the village's current time: it gives the date for seasons when only a
    weekday is given, and the time zone a full date and time is read in.
    Raises ValueError for any other format.
    """
    weekday_and_time = _WEEKDAY_AND_TIME.fullmatch(value)
    if weekday_and_time:
        return OpeningQuery(
            weekday=int(weekday_and_time["weekday"]),
            at=time.fromisoformat(weekday_and_time["at"]),
            reference_date=now.date(),
        )
    if _DATE_AND_TIME.fullmatch(value):
        moment = _in_village_time(datetime.fromisoformat(value), now)
        return OpeningQuery(
            weekday=moment.isoweekday(), at=moment.time(), reference_date=moment.date()
        )
    raise ValueError(f"Unsupported abierto_en value: {value!r}")


def _in_village_time(moment: datetime, now: datetime) -> datetime:
    if moment.tzinfo is None:
        return moment.replace(tzinfo=now.tzinfo)
    return moment.astimezone(now.tzinfo)
