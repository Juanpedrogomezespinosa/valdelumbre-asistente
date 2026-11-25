from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from app.assistant.interpretation.opening_time import opening_query_in
from app.domain.opening_query import OpeningQuery
from app.domain.text_folding import fold

# A Wednesday.
NOW = datetime(2026, 11, 25, 10, 20, tzinfo=ZoneInfo("Europe/Madrid"))
TODAY = date(2026, 11, 25)
WEDNESDAY = 3


def query(question: str) -> OpeningQuery | None:
    return opening_query_in(fold(question), NOW)


@pytest.mark.parametrize(
    ("question", "weekday", "at"),
    [
        ("¿Qué está abierto un lunes a las 12:00?", 1, time(12, 0)),
        ("¿Qué abre el sábado a las 9.30?", 6, time(9, 30)),
        ("¿Y los domingos a las 17h?", 7, time(17, 0)),
        ("El viernes a las 5 de la tarde", 5, time(17, 0)),
        ("What is open on Monday at 12:00?", 1, time(12, 0)),
        ("Anything open on Sunday at 5pm?", 7, time(17, 0)),
        ("Open on saturday at 10 am", 6, time(10, 0)),
        ("¿Qué hay abierto el martes a mediodía?", 2, time(12, 0)),
    ],
)
def test_reads_weekday_and_time(question: str, weekday: int, at: time) -> None:
    assert query(question) == OpeningQuery(weekday=weekday, at=at, reference_date=TODAY)


@pytest.mark.parametrize("question", ["¿Qué abre el domingo?", "What opens on Sunday?"])
def test_a_weekday_without_time_means_any_time_that_day(question: str) -> None:
    assert query(question) == OpeningQuery(weekday=7, at=None, reference_date=TODAY)


@pytest.mark.parametrize("question", ["¿Qué hay abierto a las 20:00?", "Open at 8pm?"])
def test_a_time_without_weekday_means_today(question: str) -> None:
    assert query(question) == OpeningQuery(weekday=WEDNESDAY, at=time(20, 0), reference_date=TODAY)


@pytest.mark.parametrize("question", ["¿Qué está abierto ahora?", "What is open right now?"])
def test_now_uses_the_clock(question: str) -> None:
    assert query(question) == OpeningQuery(weekday=WEDNESDAY, at=time(10, 20), reference_date=TODAY)


@pytest.mark.parametrize("question", ["¿Qué abre hoy?", "Anything open today?"])
def test_today_means_any_time_today(question: str) -> None:
    assert query(question) == OpeningQuery(weekday=WEDNESDAY, at=None, reference_date=TODAY)


@pytest.mark.parametrize(
    "question",
    [
        "¿Dónde puedo probar vino de la zona?",
        "Hay 4 plazas de aparcamiento",
        "Something to do with kids outdoors?",
        "Un sendero de 7 km",
    ],
)
def test_questions_without_a_moment_have_no_opening_query(question: str) -> None:
    assert query(question) is None
