import pytest

from app.assistant.interpretation.unrecorded import unrecorded_in
from app.domain.text_folding import fold


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("hay wifi en el parque?", {"wifi"}),
        ("Is there wi-fi?", {"wifi"}),
        ("¿Admiten perros en el museo?", {"mascotas"}),
        ("Can I bring my dog?", {"mascotas"}),
        ("¿Hay baños en la plaza?", {"aseos"}),
        ("Where are the toilets?", {"aseos"}),
        ("¿Se puede pagar con tarjeta?", {"pago"}),
        ("¿Hay que reservar en la bodega?", {"reservas"}),
        ("¿Hacen visitas guiadas?", {"visitas_guiadas"}),
        ("¿Tiene terraza el restaurante?", {"terraza"}),
        ("¿Hay cajero cerca?", {"cajero"}),
        ("¿Tienen menú vegano o sin gluten?", {"dietas"}),
        ("Wifi and dogs?", {"wifi", "mascotas"}),
    ],
)
def test_recognises_what_the_assistant_does_not_look_up(question: str, expected: set[str]) -> None:
    assert unrecorded_in(fold(question)) == expected


@pytest.mark.parametrize(
    "question",
    ["¿Qué museos son accesibles?", "Bañarse en verano", "¿Dónde puedo probar vino?"],
)
def test_ordinary_questions_mention_nothing_unrecorded(question: str) -> None:
    assert unrecorded_in(fold(question)) == frozenset()
