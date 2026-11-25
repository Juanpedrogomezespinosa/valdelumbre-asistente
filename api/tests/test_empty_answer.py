from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.assistant.empty_answer import empty_answer
from app.assistant.interpretation.interpretation import interpret
from app.domain.localized_text import Language, LocalizedText
from tests.poi_factory import make_poi

NOW = datetime(2026, 11, 25, 10, 0, tzinfo=ZoneInfo("Europe/Madrid"))
CASTLE = make_poi(
    "poi-001", name=LocalizedText(es="Castillo de Valdelumbre", en="Valdelumbre Castle")
)


@pytest.mark.parametrize(
    ("question", "language", "expected"),
    [
        (
            "Quiero ver monumentos que sean accesibles",
            Language.ES,
            "Ningún lugar del catálogo cumple todo lo que buscas (monumento · accesible).",
        ),
        (
            "Accessible monuments",
            Language.EN,
            "No place in the catalogue matches everything you asked for (monument · accessible).",
        ),
        (
            "Museos o rutas abiertos el lunes a las 12:00",
            Language.ES,
            "Ningún lugar del catálogo cumple todo lo que buscas "
            "(museo o ruta · abierto el lunes a las 12:00).",
        ),
        (
            "Something open on Sunday",
            Language.EN,
            "No place in the catalogue matches everything you asked for (open on Sunday).",
        ),
    ],
)
def test_says_what_was_understood_when_no_place_matches(
    question: str, language: Language, expected: str
) -> None:
    answer = empty_answer(interpret(question, NOW), [], language)

    assert answer.text == expected
    assert answer.poi_ids == ()


def test_says_when_a_named_place_does_not_match() -> None:
    answer = empty_answer(interpret("¿Es accesible el castillo?", NOW), [CASTLE], Language.ES)

    assert answer.text == (
        "En el catálogo no consta que Castillo de Valdelumbre cumpla lo que buscas (accesible)."
    )
    assert answer.poi_ids == ()


def test_says_when_a_named_place_does_not_match_in_english() -> None:
    answer = empty_answer(interpret("Is the castle accessible?", NOW), [CASTLE], Language.EN)

    assert answer.text == (
        "The catalogue does not list Valdelumbre Castle as matching what you asked for "
        "(accessible)."
    )


def test_keeps_saying_it_has_no_information_when_nothing_was_understood() -> None:
    answer = empty_answer(interpret("¿Hay tirolina?", NOW), [], Language.ES)

    assert answer.text.startswith("No tengo información sobre eso en el catálogo de Valdelumbre.")
