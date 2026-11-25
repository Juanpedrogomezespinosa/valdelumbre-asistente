from decimal import Decimal

import pytest

from app.domain.localized_text import Language
from app.domain.price import Price
from app.routes.presenters.price_text import price_text


@pytest.mark.parametrize(
    ("price", "spanish", "english"),
    [
        (Price.free(), "Gratis", "Free"),
        (Price.fixed(Decimal("4.5")), "4,50 €", "€4.50"),
        (Price.fixed(Decimal(15)), "15 €", "€15"),
        (Price.between(Decimal(25), Decimal(35)), "25\u201335 €", "€25\u201335"),
        (Price.unknown(), "Sin datos", "No data"),
    ],
)
def test_price_is_written_as_each_language_expects(
    price: Price, spanish: str, english: str
) -> None:
    assert price_text(price, Language.ES) == spanish
    assert price_text(price, Language.EN) == english
