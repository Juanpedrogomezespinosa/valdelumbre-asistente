from datetime import time

from app.assistant import template_texts as texts
from app.domain.localized_text import Language
from app.domain.schedule import ISO_WEEKDAYS, Schedule, Season, TimeSlot

_EVERY_DAY = {Language.ES: "todos los días", Language.EN: "every day"}
_ANY_TIME = {Language.ES: "a cualquier hora", Language.EN: "at any time"}
# A run of at least three days reads better as a range ("lunes a viernes") than as a list.
_SHORTEST_RANGE = 3


def opening_hours(
    schedule: Schedule, language: Language, *, with_seasons: bool = False
) -> str | None:
    """Hours in words, or None when unknown: unknown hours are not invented (D-009).

    Without `with_seasons`, seasonal hours also give None: a short mention cannot say which
    season applies, so it leaves them out rather than state them for the wrong one.
    """
    if schedule.always_open:
        return _ANY_TIME[language]
    has_seasons = any(slot.season for slot in schedule.slots)
    if not schedule.slots or (has_seasons and not with_seasons):
        return None
    return texts.join([_group(group, language) for group in _by_days(schedule.slots)], language)


def _by_days(slots: tuple[TimeSlot, ...]) -> list[list[TimeSlot]]:
    """Slots on the same days and season, so the days are said once ("10-14 and 17-20")."""
    groups: dict[tuple[frozenset[int], Season | None], list[TimeSlot]] = {}
    for slot in slots:
        groups.setdefault((slot.weekdays, slot.season), []).append(slot)
    return list(groups.values())


def _group(slots: list[TimeSlot], language: Language) -> str:
    first = slots[0]
    days = _days(sorted(first.weekdays), language)
    if language is Language.EN:
        times = " and ".join(f"{_clock(s.opens)} to {_clock(s.closes)}" for s in slots)
        hours = f"{days}, {times}"
    else:
        times = " y ".join(f"de {_clock(s.opens)} a {_clock(s.closes)}" for s in slots)
        hours = f"{days} {times}"
    return f"{hours}, {texts.season(first.season, language)}" if first.season else hours


def _days(days: list[int], language: Language) -> str:
    if days == list(ISO_WEEKDAYS):
        return _EVERY_DAY[language]
    first, last = texts.weekday(days[0], language), texts.weekday(days[-1], language)
    if len(days) >= _SHORTEST_RANGE and days == list(range(days[0], days[-1] + 1)):
        return f"{first} to {last}" if language is Language.EN else f"de {first} a {last}"
    return texts.join([texts.weekday(day, language) for day in days], language)


def _clock(moment: time) -> str:
    return f"{moment.hour}:{moment.minute:02d}"
