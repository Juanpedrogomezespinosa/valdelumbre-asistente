from decimal import Decimal

import pytest

from app.domain.price import Price


def test_unknown_price_has_no_bounds() -> None:
    price = Price.unknown()

    assert price.is_unknown
    assert not price.is_free


def test_free_price_costs_nothing() -> None:
    price = Price.free()

    assert price.is_free
    assert not price.is_unknown


def test_a_fixed_price_of_zero_is_free() -> None:
    assert Price.fixed(Decimal(0)).is_free


def test_range_keeps_both_bounds() -> None:
    price = Price.between(Decimal(25), Decimal(35))

    assert (price.min_eur, price.max_eur) == (Decimal(25), Decimal(35))
    assert not price.is_free


def test_price_cannot_be_negative() -> None:
    with pytest.raises(ValueError, match="negative"):
        Price.fixed(Decimal(-1))


def test_range_lower_bound_cannot_exceed_upper_bound() -> None:
    with pytest.raises(ValueError, match="lower bound"):
        Price.between(Decimal(35), Decimal(25))


def test_price_needs_both_bounds_or_none() -> None:
    with pytest.raises(ValueError, match="both bounds"):
        Price(min_eur=Decimal(5), max_eur=None)
