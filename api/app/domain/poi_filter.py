from collections.abc import Iterable, Set
from dataclasses import dataclass

from app.domain.opening_query import OpeningQuery
from app.domain.poi import Category, Poi


@dataclass(frozen=True)
class PoiCriteria:
    """Structured filters shared by `GET /pois` and `/preguntar` (D-005). None means any."""

    categories: Set[Category] | None = None
    accessible: bool | None = None
    open_at: OpeningQuery | None = None


def filter_pois(pois: Iterable[Poi], criteria: PoiCriteria) -> list[Poi]:
    return [poi for poi in pois if _matches(poi, criteria)]


def _matches(poi: Poi, criteria: PoiCriteria) -> bool:
    if criteria.categories is not None and poi.category not in criteria.categories:
        return False
    # Unknown accessibility matches neither true nor false (D-008).
    if criteria.accessible is not None and poi.accessible is not criteria.accessible:
        return False
    return criteria.open_at is None or _is_known_open(poi, criteria.open_at)


def _is_known_open(poi: Poi, query: OpeningQuery) -> bool:
    schedule = poi.schedule
    if query.at is None:
        is_open = schedule.opens_on(query.weekday, query.reference_date)
    else:
        is_open = schedule.is_open(query.weekday, query.at, query.reference_date)
    # Unknown hours (None) never count as open (D-009).
    return is_open is True
