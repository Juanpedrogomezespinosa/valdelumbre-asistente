import pytest

from app.assistant.introduction_check import names_only_known_places

KNOWN = ["Museo del Aceite", "Centro de Interpretación del Valle", "Ruta del Río Lumbre"]
QUESTION = "Voy en silla de ruedas, ¿qué museos puedo visitar?"


@pytest.mark.parametrize(
    "introduction",
    [
        "Hay dos museos accesibles: el Museo del Aceite y el Centro de Interpretación del Valle.",
        "En Valdelumbre tienes dos museos accesibles. ¡Disfruta!",
        "There are two museums you can visit.",
        "Puedes pasear junto al río Lumbre.",
    ],
)
def test_accepts_names_from_the_places_the_question_or_the_village(introduction: str) -> None:
    assert names_only_known_places(introduction, QUESTION, KNOWN)


@pytest.mark.parametrize(
    "introduction",
    [
        "Hay dos museos accesibles para visitar en Valmundo.",
        "En Valmuel, puedes disfrutar de vinos locales.",
        "El Castillo de Valdelumbre está cerrado, pero los museos no.",
    ],
    ids=["invented village", "invented village after comma", "place not retrieved"],
)
def test_rejects_any_other_proper_name(introduction: str) -> None:
    assert not names_only_known_places(introduction, QUESTION, KNOWN)
