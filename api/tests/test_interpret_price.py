from decimal import Decimal

import pytest

from app.assistant.interpretation.price import price_under, wants_cheapest, wants_free
from app.domain.text_folding import fold


@pytest.mark.parametrize(
    "question",
    [
        "¿Qué es gratis?",
        "Sitios gratuitos",
        "que puedo hacer sin dinero?",
        "que puedo hacer sin gastar dinero?",
        "Planes sin gastar nada",
        "Algo sin pagar",
        "Sin coste",
        "¿Qué no cuesta nada?",
        "Free things to do",
        "Things to do without spending money",
        "Places with no money",
        "What costs nothing?",
    ],
)
def test_asks_for_free_places(question: str) -> None:
    assert wants_free(fold(question))


@pytest.mark.parametrize(
    "question",
    ["Is there free wifi?", "¿Hay wifi gratis?", "Gluten free menu", "¿Cuánto cuesta el castillo?"],
)
def test_free_that_is_not_about_the_price(question: str) -> None:
    assert not wants_free(fold(question))


@pytest.mark.parametrize(
    ("question", "amount"),
    [
        ("¿Qué cuesta menos de 5 euros?", Decimal(5)),
        ("Places under 4,5 €", Decimal("4.5")),
        ("Algo por menos de 10 €", Decimal(10)),
    ],
)
def test_reads_a_maximum_price(question: str, amount: Decimal) -> None:
    assert price_under(fold(question)) == amount


def test_a_number_without_a_price_word_is_not_a_price() -> None:
    assert price_under(fold("Abierto hasta 5 personas")) is None


def test_asks_for_the_cheapest() -> None:
    assert wants_cheapest(fold("¿Qué es lo más barato?"))
    assert wants_cheapest(fold("The cheapest museum"))
