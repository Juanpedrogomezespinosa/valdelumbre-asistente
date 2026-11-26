from collections.abc import Iterable
from datetime import time

import pytest

from app.assistant.tourist_office import find_tourist_office, referral
from app.domain.localized_text import Language, LocalizedText
from app.domain.poi import Category, Poi
from app.domain.schedule import Schedule, Season, TimeSlot
from tests.poi_factory import make_poi

EVERY_DAY = frozenset(range(1, 8))
CASTLE = make_poi("poi-001", name=LocalizedText(es="Castillo", en="Castle"))


def office(schedule: Schedule) -> Poi:
    return make_poi(
        "poi-010",
        name=LocalizedText(es="Oficina de Turismo", en="Tourist Office"),
        category=Category.SERVICE,
        schedule=schedule,
    )


def slot(days: Iterable[int], opens: str, closes: str, season: Season | None = None) -> TimeSlot:
    return TimeSlot(
        weekdays=frozenset(days),
        opens=time.fromisoformat(opens),
        closes=time.fromisoformat(closes),
        season=season,
    )


MORNINGS = Schedule(always_open=False, slots=(slot(EVERY_DAY, "09:30", "14:30"),))


def test_finds_the_tourist_office_by_its_name_in_either_language() -> None:
    spanish_only = make_poi("a", name=LocalizedText(es="Oficina de turismo municipal"))
    english_only = make_poi("b", name=LocalizedText(es="Punto de información", en="Tourist Office"))

    assert find_tourist_office([CASTLE, spanish_only]) == spanish_only
    assert find_tourist_office([english_only, CASTLE]) == english_only


def test_without_a_tourist_office_in_the_catalog_there_is_nothing_to_refer_to() -> None:
    assert find_tourist_office([CASTLE]) is None
    assert referral(None, Language.ES) is None


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        (Language.ES, "pregunta en la Oficina de Turismo (todos los días de 9:30 a 14:30)"),
        (Language.EN, "ask at the Tourist Office (every day, 9:30 to 14:30)"),
    ],
)
def test_refers_to_the_office_with_its_opening_hours(language: Language, expected: str) -> None:
    assert referral(office(MORNINGS), language) == expected


@pytest.mark.parametrize(
    ("days", "spanish", "english"),
    [
        ({1, 2, 3, 4, 5}, "de lunes a viernes de 9:00 a 14:00", "Monday to Friday, 9:00 to 14:00"),
        ({1, 3}, "lunes y miércoles de 9:00 a 14:00", "Monday and Wednesday, 9:00 to 14:00"),
        ({6}, "sábado de 9:00 a 14:00", "Saturday, 9:00 to 14:00"),
    ],
)
def test_names_the_opening_days(days: set[int], spanish: str, english: str) -> None:
    schedule = Schedule(always_open=False, slots=(slot(days, "09:00", "14:00"),))

    assert (
        referral(office(schedule), Language.ES) == f"pregunta en la Oficina de Turismo ({spanish})"
    )
    assert referral(office(schedule), Language.EN) == f"ask at the Tourist Office ({english})"


def test_joins_several_slots() -> None:
    schedule = Schedule(
        always_open=False,
        slots=(slot({1, 2, 3, 4, 5}, "09:00", "14:00"), slot({6}, "10:00", "13:00")),
    )

    assert referral(office(schedule), Language.ES) == (
        "pregunta en la Oficina de Turismo "
        "(de lunes a viernes de 9:00 a 14:00 y sábado de 10:00 a 13:00)"
    )


def test_always_open_says_so() -> None:
    always = Schedule(always_open=True, slots=())

    assert referral(office(always), Language.ES) == (
        "pregunta en la Oficina de Turismo (a cualquier hora)"
    )
    assert referral(office(always), Language.EN) == "ask at the Tourist Office (at any time)"


@pytest.mark.parametrize(
    "schedule",
    [
        Schedule(always_open=False, slots=()),
        Schedule(
            always_open=False,
            slots=(slot(EVERY_DAY, "09:00", "14:00", Season(start=(6, 1), end=(9, 30))),),
        ),
    ],
    ids=["unknown hours", "seasonal hours"],
)
def test_names_the_office_without_hours_it_cannot_state_simply(schedule: Schedule) -> None:
    # Unknown hours are not invented (D-009); seasonal ones would need today's date to be right.
    assert referral(office(schedule), Language.ES) == "pregunta en la Oficina de Turismo"


def test_slots_on_the_same_days_share_the_days() -> None:
    weekdays = {1, 2, 3, 4, 5, 6}
    schedule = Schedule(
        always_open=False,
        slots=(slot(weekdays, "10:00", "14:00"), slot(weekdays, "17:00", "20:00")),
    )

    assert referral(office(schedule), Language.ES) == (
        "pregunta en la Oficina de Turismo (de lunes a sábado de 10:00 a 14:00 y de 17:00 a 20:00)"
    )
    assert referral(office(schedule), Language.EN) == (
        "ask at the Tourist Office (Monday to Saturday, 10:00 to 14:00 and 17:00 to 20:00)"
    )
