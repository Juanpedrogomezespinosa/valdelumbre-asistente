from decimal import Decimal

import pytest

from app.data.normalization import RawPrice, normalize_price
from app.data.quality import WarningKind
from app.domain.price import Price


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0, Price.free()),
        (4.5, Price.fixed(Decimal("4.5"))),
        (15, Price.fixed(Decimal(15))),
        ("gratis", Price.free()),
        (" Gratis ", Price.free()),
        ("free", Price.free()),
        ("4,5", Price.fixed(Decimal("4.5"))),
        ("25-35", Price.between(Decimal(25), Decimal(35))),
        ("25 \u2013 35 €", Price.between(Decimal(25), Decimal(35))),
    ],
)
def test_heterogeneous_prices_are_normalized(raw: RawPrice, expected: Price) -> None:
    price, warnings = normalize_price("poi-x", raw)

    assert price == expected
    assert warnings == []


def test_missing_price_is_unknown_without_warning() -> None:
    price, warnings = normalize_price("poi-x", None)

    assert price.is_unknown
    assert warnings == []


@pytest.mark.parametrize("raw", ["consultar", -3, "35-25", True])
def test_unparseable_price_becomes_unknown_with_warning(raw: RawPrice) -> None:
    price, warnings = normalize_price("poi-x", raw)

    assert price.is_unknown
    assert [(w.poi_id, w.kind) for w in warnings] == [("poi-x", WarningKind.UNPARSEABLE_PRICE)]
