import pytest

from app.assistant.interpretation.accessibility import wants_accessible
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
    assert wants_accessible(fold(question)) is True


@pytest.mark.parametrize(
    "question",
    ["¿Qué museos hay?", "Something to do with kids outdoors?", "¿Dónde puedo comer?"],
)
def test_ignores_questions_without_accessibility_needs(question: str) -> None:
    assert wants_accessible(fold(question)) is False
