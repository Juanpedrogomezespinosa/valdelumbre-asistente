import json
from pathlib import Path

from app.data.quality import WarningKind
from app.data.rules.coordinates import normalize_coordinates
from app.domain.coordinates import Coordinates

POIS_PATH = Path(__file__).resolve().parents[2] / "datos" / "pois.json"

VILLAGE = {
    "castle": (40.4172, -3.7051),
    "square": (40.4168, -3.7038),
    "park": (40.418, -3.702),
    "winery": (40.405, -3.73),
}


def test_coordinates_consistent_with_the_catalog_are_kept() -> None:
    coordinates, warnings = normalize_coordinates(VILLAGE)

    assert coordinates["castle"] == Coordinates(lat=40.4172, lon=-3.7051)
    assert warnings == []


def test_swapped_coordinates_are_swapped_back_with_warning() -> None:
    coordinates, warnings = normalize_coordinates({**VILLAGE, "bridge": (-3.711, 40.421)})

    assert coordinates["bridge"] == Coordinates(lat=40.421, lon=-3.711)
    assert [(w.poi_id, w.kind) for w in warnings] == [("bridge", WarningKind.SWAPPED_COORDINATES)]


def test_coordinates_far_from_the_catalog_are_dropped_with_warning() -> None:
    coordinates, warnings = normalize_coordinates({**VILLAGE, "null_island": (0.0, 0.0)})

    assert coordinates["null_island"] is None
    assert [(w.poi_id, w.kind) for w in warnings] == [
        ("null_island", WarningKind.OUTLIER_COORDINATES)
    ]


def test_coordinates_outside_the_globe_are_dropped_with_warning() -> None:
    coordinates, warnings = normalize_coordinates({**VILLAGE, "nowhere": (200.0, 300.0)})

    assert coordinates["nowhere"] is None
    assert [w.kind for w in warnings] == [WarningKind.OUTLIER_COORDINATES]


def test_only_the_roman_bridge_is_swapped_in_the_real_catalog() -> None:
    pois = json.loads(POIS_PATH.read_text(encoding="utf-8"))
    raw = {poi["id"]: (poi["lat"], poi["lon"]) for poi in pois}

    coordinates, warnings = normalize_coordinates(raw)

    assert [(w.poi_id, w.kind) for w in warnings] == [("poi-011", WarningKind.SWAPPED_COORDINATES)]
    assert coordinates["poi-011"] == Coordinates(lat=40.421, lon=-3.711)
