from datetime import date, time

import pytest

from app.domain.localized_text import LocalizedText
from app.domain.opening_query import OpeningQuery
from app.domain.poi import Category, Poi
from app.domain.poi_filter import PoiCriteria, filter_pois
from app.domain.price import Price
from app.domain.schedule import Schedule, TimeSlot

ALWAYS_OPEN = Schedule(always_open=True, slots=())
UNKNOWN_HOURS = Schedule(always_open=False, slots=())
WEEKEND_MORNINGS = Schedule(
    always_open=False, slots=(TimeSlot(frozenset({6, 7}), time(10, 0), time(14, 0)),)
)
MONDAY_AT_NOON = OpeningQuery(weekday=1, at=time(12, 0), reference_date=date(2026, 11, 23))


def poi(
    poi_id: str,
    category: Category = Category.MONUMENT,
    accessible: bool | None = None,
    schedule: Schedule = ALWAYS_OPEN,
) -> Poi:
    return Poi(
        id=poi_id,
        name=LocalizedText(es=poi_id),
        category=category,
        description=LocalizedText(es=""),
        coordinates=None,
        accessible=accessible,
        schedule=schedule,
        price=Price.unknown(),
        tags=(),
    )


def ids(pois: list[Poi]) -> list[str]:
    return [p.id for p in pois]


def test_without_criteria_keeps_every_poi_in_catalog_order() -> None:
    catalog = [poi("b"), poi("a"), poi("c")]

    assert ids(filter_pois(catalog, PoiCriteria())) == ["b", "a", "c"]


def test_filters_by_category() -> None:
    catalog = [poi("castle", Category.MONUMENT), poi("museum", Category.MUSEUM)]

    assert ids(filter_pois(catalog, PoiCriteria(categories={Category.MUSEUM}))) == ["museum"]


def test_several_categories_match_any_of_them() -> None:
    catalog = [
        poi("park", Category.NATURE),
        poi("museum", Category.MUSEUM),
        poi("trail", Category.ROUTE),
    ]
    outdoors = PoiCriteria(categories={Category.NATURE, Category.ROUTE})

    assert ids(filter_pois(catalog, outdoors)) == ["park", "trail"]


@pytest.mark.parametrize(("wanted", "expected"), [(True, ["yes"]), (False, ["no"])])
def test_accessibility_filter_never_includes_unknown(wanted: bool, expected: list[str]) -> None:
    catalog = [poi("yes", accessible=True), poi("no", accessible=False), poi("unknown")]

    assert ids(filter_pois(catalog, PoiCriteria(accessible=wanted))) == expected


def test_open_at_keeps_only_pois_known_to_be_open() -> None:
    catalog = [
        poi("always", schedule=ALWAYS_OPEN),
        poi("weekends", schedule=WEEKEND_MORNINGS),
        poi("unknown", schedule=UNKNOWN_HOURS),
    ]

    assert ids(filter_pois(catalog, PoiCriteria(open_at=MONDAY_AT_NOON))) == ["always"]


def test_criteria_are_combined() -> None:
    catalog = [
        poi("match", Category.MUSEUM, accessible=True),
        poi("wrong-category", Category.MONUMENT, accessible=True),
        poi("not-accessible", Category.MUSEUM, accessible=False),
        poi("closed", Category.MUSEUM, accessible=True, schedule=WEEKEND_MORNINGS),
    ]
    criteria = PoiCriteria(categories={Category.MUSEUM}, accessible=True, open_at=MONDAY_AT_NOON)

    assert ids(filter_pois(catalog, criteria)) == ["match"]


def test_open_on_a_whole_day_keeps_pois_that_open_at_some_time_that_day() -> None:
    catalog = [
        poi("always", schedule=ALWAYS_OPEN),
        poi("weekends", schedule=WEEKEND_MORNINGS),
        poi("unknown", schedule=UNKNOWN_HOURS),
    ]
    saturday = OpeningQuery(weekday=6, at=None, reference_date=date(2026, 11, 28))

    assert ids(filter_pois(catalog, PoiCriteria(open_at=saturday))) == ["always", "weekends"]


@pytest.mark.parametrize("weekday", [0, 8])
def test_opening_query_rejects_non_iso_weekdays(weekday: int) -> None:
    with pytest.raises(ValueError, match="ISO weekday"):
        OpeningQuery(weekday=weekday, at=time(12, 0), reference_date=date(2026, 11, 23))
