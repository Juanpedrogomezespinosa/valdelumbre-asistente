import re
from datetime import datetime, time, timedelta

from app.assistant.interpretation.phrases import contains_any
from app.domain.opening_query import OpeningQuery

_WEEKDAY_NAMES: dict[str, int] = {
    name: weekday
    for weekday, names in enumerate(
        (
            ("lunes", "monday", "mondays"),
            ("martes", "tuesday", "tuesdays"),
            ("miercoles", "wednesday", "wednesdays"),
            ("jueves", "thursday", "thursdays"),
            ("viernes", "friday", "fridays"),
            ("sabado", "sabados", "saturday", "saturdays"),
            ("domingo", "domingos", "sunday", "sundays"),
        ),
        start=1,
    )
    for name in names
}
_NOW = ("ahora", "en este momento", "now", "right now")
_TODAY = ("hoy", "today")
_NOON = ("mediodia", "noon", "midday")
_AFTERNOON = ("de la tarde", "de la noche")
_OPENING = ("abierto", "abierta", "abiertos", "abre", "abren", "open", "opens", "hora", "horas")
# A part of the day is checked at one representative time, inside usual opening hours.
_PARTS_OF_DAY = {
    time(10, 0): (
        "por la manana",
        "esta manana",
        "de manana",
        "in the morning",
        "this morning",
    ),
    time(17, 0): ("por la tarde", "esta tarde", "in the afternoon", "this afternoon"),
    time(21, 0): (
        "por la noche",
        "esta noche",
        "de noche",
        "tonight",
        "in the evening",
        "this evening",
    ),
}
# "Mañana" alone is tomorrow; "por la mañana" is the morning.
_TOMORROW = re.compile(r"\btomorrow\b|(?<!la )(?<!esta )(?<!de )\bmanana\b")

TIME_WORDS = (
    *_WEEKDAY_NAMES,
    *_NOW,
    *_TODAY,
    *_NOON,
    *_AFTERNOON,
    *_OPENING,
    *(phrase for phrases in _PARTS_OF_DAY.values() for phrase in phrases),
    "hour",
    "hours",
    "manana",
    "tomorrow",
)

_WEEKDAY = re.compile(rf"\b({'|'.join(_WEEKDAY_NAMES)})\b")
_CLOCK = re.compile(r"\b(?P<hour>\d{1,2})[:.](?P<minute>\d{2})\b")
_MERIDIEM = re.compile(r"\b(?P<hour>\d{1,2})\s*(?P<meridiem>[ap])\.?m\b")
_HOURS = re.compile(r"\b(?P<hour>\d{1,2})\s*h\b")
_AT_HOUR = re.compile(r"\b(?:a las|a la|at)\s+(?P<hour>\d{1,2})\b")


def opening_query_in(folded: str, now: datetime) -> OpeningQuery | None:
    """The moment a question asks about, if any. Seasons use today's date (D-011)."""
    if contains_any(folded, _NOW):
        return now_query(now)
    day = now.date() + timedelta(days=1) if _TOMORROW.search(folded) else now.date()
    weekday = _weekday_in(folded)
    at = _time_in(folded) or _part_of_day_in(folded)
    if weekday is None and at is None and day == now.date() and not contains_any(folded, _TODAY):
        return None
    return OpeningQuery(weekday=weekday or day.isoweekday(), at=at, reference_date=day)


def now_query(now: datetime) -> OpeningQuery:
    return OpeningQuery(weekday=now.isoweekday(), at=now.time(), reference_date=now.date())


def _weekday_in(folded: str) -> int | None:
    match = _WEEKDAY.search(folded)
    return None if match is None else _WEEKDAY_NAMES[match[1]]


def _time_in(folded: str) -> time | None:
    if contains_any(folded, _NOON):
        return time(12, 0)
    if clock := _CLOCK.search(folded):
        return _valid_time(_afternoon(folded, int(clock["hour"])), int(clock["minute"]))
    if meridiem := _MERIDIEM.search(folded):
        hour = int(meridiem["hour"]) % 12 + (12 if meridiem["meridiem"] == "p" else 0)
        return _valid_time(hour, 0)
    if hours := _HOURS.search(folded) or _AT_HOUR.search(folded):
        return _valid_time(_afternoon(folded, int(hours["hour"])), 0)
    return None


def _part_of_day_in(folded: str) -> time | None:
    return next(
        (at for at, phrases in _PARTS_OF_DAY.items() if contains_any(folded, phrases)), None
    )


def _afternoon(folded: str, hour: int) -> int:
    return hour + 12 if hour < 12 and contains_any(folded, _AFTERNOON) else hour


def _valid_time(hour: int, minute: int) -> time | None:
    if hour > 23 or minute > 59:
        return None
    return time(hour, minute)
