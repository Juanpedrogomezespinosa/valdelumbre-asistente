import pytest

from app.assistant.interpretation.accessibility import accessibility_in
from app.domain.text_folding import fold


@pytest.mark.parametrize(
    "question",
    [
        "Voy en silla de ruedas, ¿qué puedo visitar?",
        "¿Qué sitios son accesibles?",
        "Información de accesibilidad",
        "Viajo con una persona con movilidad reducida",
        "I use a wheelchair, where can I go?",
        "Which places are accessible?",
        "Places for people with reduced mobility",
    ],
)
def test_detects_accessibility_needs(question: str) -> None:
    assert accessibility_in(fold(question)) == (True, False)


@pytest.mark.parametrize(
    "question",
    ["¿Qué museos hay?", "Something to do with kids outdoors?", "¿Dónde puedo comer?"],
)
def test_ignores_questions_without_accessibility_needs(question: str) -> None:
    assert accessibility_in(fold(question)) == (None, False)


@pytest.mark.parametrize(
    "question",
    [
        "¿Qué sitios no son accesibles?",
        "Lugares no accesibles",
        "Which places are not accessible?",
        "Which places aren't wheelchair accessible?",
        "Inaccessible places",
    ],
)
def test_a_negation_asks_for_places_that_are_not_accessible(question: str) -> None:
    assert accessibility_in(fold(question)) == (False, False)


@pytest.mark.parametrize(
    "question",
    ["¿Qué lugares no tienen datos de accesibilidad?", "Places with no accessibility data"],
)
def test_asks_for_places_with_unknown_accessibility(question: str) -> None:
    assert accessibility_in(fold(question)) == (None, True)
