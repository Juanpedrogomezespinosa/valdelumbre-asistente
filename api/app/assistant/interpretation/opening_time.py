import re
from datetime import datetime, time

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

TIME_WORDS = (*_WEEKDAY_NAMES, *_NOW, *_TODAY, *_NOON, *_AFTERNOON, *_OPENING, "hour", "hours")

_WEEKDAY = re.compile(rf"\b({'|'.join(_WEEKDAY_NAMES)})\b")
_CLOCK = re.compile(r"\b(?P<hour>\d{1,2})[:.](?P<minute>\d{2})\b")
_MERIDIEM = re.compile(r"\b(?P<hour>\d{1,2})\s*(?P<meridiem>[ap])\.?m\b")
_HOURS = re.compile(r"\b(?P<hour>\d{1,2})\s*h\b")
_AT_HOUR = re.compile(r"\b(?:a las|a la|at)\s+(?P<hour>\d{1,2})\b")


def opening_query_in(folded: str, now: datetime) -> OpeningQuery | None:
    """The moment a question asks about, if any. Seasons use today's date (D-011)."""
    if contains_any(folded, _NOW):
        return OpeningQuery(weekday=now.isoweekday(), at=now.time(), reference_date=now.date())
    weekday = _weekday_in(folded)
    at = _time_in(folded)
    if weekday is None and at is None and not contains_any(folded, _TODAY):
        return None
    return OpeningQuery(weekday=weekday or now.isoweekday(), at=at, reference_date=now.date())


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


def _afternoon(folded: str, hour: int) -> int:
    return hour + 12 if hour < 12 and contains_any(folded, _AFTERNOON) else hour


def _valid_time(hour: int, minute: int) -> time | None:
    if hour > 23 or minute > 59:
        return None
    return time(hour, minute)
