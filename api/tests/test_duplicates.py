from dataclasses import replace
from datetime import time

from app.data.normalization import remove_duplicates
from app.data.quality import WarningKind
from app.domain.coordinates import Coordinates
from app.domain.localized_text import LocalizedText
from app.domain.poi import Category, Poi
from app.domain.price import Price
from app.domain.schedule import Schedule, TimeSlot

OLIVE_MILL = Coordinates(lat=40.416, lon=-3.708)

OLIVE_OIL_MUSEUM = Poi(
    id="poi-003",
    name=LocalizedText(es="Museo del Aceite", en="Olive Oil Museum"),
    category=Category.MUSEUM,
    description=LocalizedText(es="Museo etnográfico.", en="Ethnographic museum."),
    coordinates=OLIVE_MILL,
    accessible=True,
    schedule=Schedule(
        always_open=False,
        slots=(TimeSlot(frozenset(range(2, 8)), time(10, 0), time(18, 0)),),
    ),
    price=Price.free(),
    tags=("historia", "familias"),
)

OLD_RECORD = Poi(
    id="poi-004",
    name=LocalizedText(es="museo del aceite"),
    category=Category.MUSEUM,
    description=LocalizedText(es="Museo del aceite (ficha antigua)."),
    coordinates=OLIVE_MILL,
    accessible=None,
    schedule=Schedule(always_open=False, slots=()),
    price=Price.unknown(),
    tags=(),
)


def ids(pois: list[Poi]) -> list[str]:
    return [poi.id for poi in pois]


def test_the_most_complete_record_is_kept_and_the_duplicate_reported() -> None:
    pois, warnings = remove_duplicates([OLIVE_OIL_MUSEUM, OLD_RECORD])

    assert ids(pois) == ["poi-003"]
    assert [(w.poi_id, w.kind) for w in warnings] == [("poi-004", WarningKind.DUPLICATE_POI)]
    assert "poi-003" in warnings[0].action


def test_the_most_complete_record_wins_whatever_the_order() -> None:
    pois, _ = remove_duplicates([OLD_RECORD, OLIVE_OIL_MUSEUM])

    assert ids(pois) == ["poi-003"]


def test_on_equal_completeness_the_first_record_is_kept() -> None:
    twin = replace(OLIVE_OIL_MUSEUM, id="poi-099")

    pois, _ = remove_duplicates([OLIVE_OIL_MUSEUM, twin])

    assert ids(pois) == ["poi-003"]


def test_same_name_in_a_different_place_is_not_a_duplicate() -> None:
    elsewhere = replace(OLD_RECORD, coordinates=Coordinates(lat=40.43, lon=-3.72))

    pois, warnings = remove_duplicates([OLIVE_OIL_MUSEUM, elsewhere])

    assert ids(pois) == ["poi-003", "poi-004"]
    assert warnings == []


def test_different_name_in_the_same_place_is_not_a_duplicate() -> None:
    shop = replace(OLD_RECORD, name=LocalizedText(es="Tienda del museo"))

    pois, warnings = remove_duplicates([OLIVE_OIL_MUSEUM, shop])

    assert ids(pois) == ["poi-003", "poi-004"]
    assert warnings == []


def test_points_without_coordinates_are_never_merged() -> None:
    first = replace(OLIVE_OIL_MUSEUM, coordinates=None)
    second = replace(OLD_RECORD, coordinates=None)

    pois, warnings = remove_duplicates([first, second])

    assert ids(pois) == ["poi-003", "poi-004"]
    assert warnings == []
