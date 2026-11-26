from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from app.assistant.empty_answer import empty_answer
from app.assistant.interpretation.interpretation import interpret
from app.domain.localized_text import Language, LocalizedText
from app.domain.poi import Category
from app.domain.schedule import Schedule, TimeSlot
from tests.poi_factory import make_poi

NOW = datetime(2026, 11, 25, 10, 0, tzinfo=ZoneInfo("Europe/Madrid"))
CASTLE = make_poi(
    "poi-001", name=LocalizedText(es="Castillo de Valdelumbre", en="Valdelumbre Castle")
)
OFFICE = make_poi(
    "poi-010",
    name=LocalizedText(es="Oficina de Turismo", en="Tourist Office"),
    category=Category.SERVICE,
    schedule=Schedule(
        always_open=False,
        slots=(TimeSlot(frozenset(range(1, 8)), time(9, 30), time(14, 30)),),
    ),
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


def test_when_nothing_was_understood_it_refers_to_the_tourist_office() -> None:
    spanish = empty_answer(interpret("¿Hay tirolina?", NOW), [], Language.ES, office=OFFICE)
    english = empty_answer(interpret("Any zipline?", NOW), [], Language.EN, office=OFFICE)

    assert spanish.text.endswith(
        "Para todo lo demás, pregunta en la Oficina de Turismo (todos los días de 9:30 a 14:30)."
    )
    assert english.text.endswith(
        "For anything else, ask at the Tourist Office (every day, 9:30 to 14:30)."
    )
    assert spanish.poi_ids == english.poi_ids == ()


def test_what_it_does_not_look_up_is_referred_to_the_tourist_office() -> None:
    answer = empty_answer(interpret("¿Se admiten perros?", NOW), [], Language.ES, office=OFFICE)

    assert answer.text == (
        "No puedo responder sobre mascotas: no es un dato que yo consulte. Mira la ficha del "
        "lugar o pregunta en la Oficina de Turismo (todos los días de 9:30 a 14:30)."
    )
    assert answer.poi_ids == ()


def test_a_question_it_understood_is_not_referred_even_with_no_match() -> None:
    # "No place matches" is already a complete answer (D-049).
    answer = empty_answer(interpret("Accessible monuments", NOW), [], Language.EN, office=OFFICE)

    assert "Tourist Office" not in answer.text


def test_without_a_tourist_office_it_does_not_mention_one() -> None:
    not_understood = empty_answer(interpret("¿Hay tirolina?", NOW), [], Language.ES)
    not_looked_up = empty_answer(interpret("¿Se admiten perros?", NOW), [], Language.ES)

    assert "Oficina" not in not_understood.text
    assert not_looked_up.text == (
        "No puedo responder sobre mascotas: no es un dato que yo consulte. Mira la ficha del lugar."
    )


@pytest.mark.parametrize(
    ("question", "language", "described"),
    [
        ("¿Qué museos están cerrados el domingo?", Language.ES, "(museo · cerrado el domingo)"),
        ("Closed museums on Sunday", Language.EN, "(museum · closed on Sunday)"),
        ("Museos gratis y no accesibles", Language.ES, "(museo · no accesible · gratis)"),
        (
            "Rutas de menos de 2 euros sin datos de accesibilidad",
            Language.ES,
            "(ruta · sin datos de accesibilidad · menos de 2 €)",
        ),
    ],
)
def test_describes_the_new_criteria_when_no_place_matches(
    question: str, language: Language, described: str
) -> None:
    answer = empty_answer(interpret(question, NOW), [], language)

    assert answer.text.endswith(f"{described}.")
