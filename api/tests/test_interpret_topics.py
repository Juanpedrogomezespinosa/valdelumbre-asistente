import pytest

from app.assistant.interpretation.topics import topics_in
from app.domain.text_folding import fold


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("¿Dónde puedo probar vino de la zona?", {"vino"}),
        ("Is there a winery?", {"vino"}),
        ("Something to do with kids outdoors?", {"familias"}),
        ("Planes con niños", {"familias"}),
        ("Un sitio con vistas para ver el atardecer", {"vistas", "atardecer"}),
        ("I like history and art", {"historia", "arte"}),
        ("¿Dónde me puedo bañar?", {"verano"}),
        ("Quiero hacer senderismo", {"senderismo"}),
        ("Me gusta la naturaleza", {"naturaleza"}),
    ],
)
def test_maps_words_to_catalog_topics(question: str, expected: set[str]) -> None:
    assert topics_in(fold(question)) == expected


def test_unknown_activities_are_not_guessed() -> None:
    assert topics_in(fold("¿Hay algún sitio de aventura con tirolina?")) == frozenset()


def test_accessibility_is_never_a_topic() -> None:
    # Accessibility comes from the structured field only (D-005), never from tags.
    assert topics_in(fold("¿Qué es accesible en silla de ruedas?")) == frozenset()
