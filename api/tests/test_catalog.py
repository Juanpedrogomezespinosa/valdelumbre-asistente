import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.data.catalog import Catalog, load_catalog
from app.data.quality import WarningKind
from app.domain.coordinates import Coordinates
from app.domain.price import Price
from app.domain.schedule import Season

POIS_PATH = Path(__file__).resolve().parents[2] / "datos" / "pois.json"


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog(POIS_PATH)


def test_the_duplicate_record_is_not_served(catalog: Catalog) -> None:
    assert len(catalog.pois) == 17
    assert catalog.get("poi-004") is None
    assert catalog.get("poi-003") is not None


def test_swapped_coordinates_are_served_fixed(catalog: Catalog) -> None:
    roman_bridge = catalog.get("poi-011")

    assert roman_bridge is not None
    assert roman_bridge.coordinates == Coordinates(lat=40.421, lon=-3.711)


def test_injected_instruction_is_not_served(catalog: Catalog) -> None:
    tapestry_house = catalog.get("poi-013")

    assert tapestry_house is not None
    assert tapestry_house.description.es == "Colección de tapices flamencos."
    assert tapestry_house.accessible is False


def test_heterogeneous_prices_are_served_normalized(catalog: Catalog) -> None:
    prices = {poi.id: poi.price for poi in catalog.pois}

    assert prices["poi-003"] == Price.free()
    assert prices["poi-009"] == Price.between(Decimal(25), Decimal(35))
    assert prices["poi-016"].is_unknown


def test_schedules_keep_seasons_and_unknowns(catalog: Catalog) -> None:
    natural_pool = catalog.get("poi-014")
    hermitage = catalog.get("poi-018")

    assert natural_pool is not None and hermitage is not None
    assert natural_pool.schedule.slots[0].season == Season(start=(6, 1), end=(9, 30))
    assert not hermitage.schedule.is_known


def test_unknown_accessibility_is_kept_as_unknown(catalog: Catalog) -> None:
    roman_bridge = catalog.get("poi-011")

    assert roman_bridge is not None
    assert roman_bridge.accessible is None


def test_every_data_defect_is_reported(catalog: Catalog) -> None:
    reported = {(warning.poi_id, warning.kind) for warning in catalog.warnings}

    assert reported == {
        ("poi-004", WarningKind.DUPLICATE_POI),
        ("poi-004", WarningKind.MISSING_TRANSLATION),
        ("poi-004", WarningKind.UNKNOWN_SCHEDULE),
        ("poi-011", WarningKind.SWAPPED_COORDINATES),
        ("poi-013", WarningKind.INJECTED_INSTRUCTION),
        ("poi-018", WarningKind.UNKNOWN_SCHEDULE),
    }


def write_catalog(tmp_path: Path, pois: list[dict[str, Any]]) -> Path:
    path = tmp_path / "pois.json"
    path.write_text(json.dumps(pois), encoding="utf-8")
    return path


def raw_poi(poi_id: str, **overrides: Any) -> dict[str, Any]:
    return {
        "id": poi_id,
        "nombre": {"es": "Plaza", "en": "Square"},
        "categoria": "espacio_publico",
        "descripcion": {"es": "Plaza.", "en": "Square."},
        "lat": 40.4168,
        "lon": -3.7038,
        "accesible": True,
        "horario": {"always_open": True, "franjas": []},
        "precio": 0,
        "etiquetas": [],
        **overrides,
    }


def test_unknown_category_stops_the_load(tmp_path: Path) -> None:
    path = write_catalog(tmp_path, [raw_poi("poi-1", categoria="zoo")])

    with pytest.raises(ValidationError, match="categoria"):
        load_catalog(path)


def test_repeated_ids_stop_the_load(tmp_path: Path) -> None:
    path = write_catalog(tmp_path, [raw_poi("poi-1"), raw_poi("poi-1")])

    with pytest.raises(ValueError, match="poi-1"):
        load_catalog(path)
