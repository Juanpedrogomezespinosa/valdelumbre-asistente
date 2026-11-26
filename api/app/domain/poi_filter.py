from collections.abc import Iterable, Set
from dataclasses import dataclass
from decimal import Decimal

from app.domain.opening_query import OpeningQuery
from app.domain.poi import Category, Poi


@dataclass(frozen=True)
class PoiCriteria:
    """Structured filters shared by `GET /pois` and `/preguntar` (D-005). None means any.

    `GET /pois` only exposes the filters the API contract names; the assistant also uses
    the rest (closed, unknown accessibility and price), always on structured fields.
    """

    categories: Set[Category] | None = None
    accessible: bool | None = None
    accessibility_unknown: bool = False
    open_at: OpeningQuery | None = None
    closed: bool = False
    """With `open_at`: keep the places known to be closed then, instead of open."""
    free: bool = False
    price_under: Decimal | None = None


def filter_pois(pois: Iterable[Poi], criteria: PoiCriteria) -> list[Poi]:
    return [poi for poi in pois if _matches(poi, criteria)]


def _matches(poi: Poi, criteria: PoiCriteria) -> bool:
    if criteria.categories is not None and poi.category not in criteria.categories:
        return False
    # Unknown accessibility matches neither true nor false (D-008).
    if criteria.accessible is not None and poi.accessible is not criteria.accessible:
        return False
    if criteria.accessibility_unknown and poi.accessible is not None:
        return False
    if not _matches_price(poi, criteria):
        return False
    if criteria.open_at is None:
        return True
    # Unknown hours (None) are neither open nor closed (D-009).
    wanted = not criteria.closed
    return _is_open(poi, criteria.open_at) is wanted


def _matches_price(poi: Poi, criteria: PoiCriteria) -> bool:
    price = poi.price
    # An unknown price matches no price filter: it might cost anything.
    if price.max_eur is None:
        return not criteria.free and criteria.price_under is None
    if criteria.free and price.max_eur != 0:
        return False
    return criteria.price_under is None or price.max_eur < criteria.price_under


def _is_open(poi: Poi, query: OpeningQuery) -> bool | None:
    schedule = poi.schedule
    if query.at is None:
        return schedule.opens_on(query.weekday, query.reference_date)
    return schedule.is_open(query.weekday, query.at, query.reference_date)
