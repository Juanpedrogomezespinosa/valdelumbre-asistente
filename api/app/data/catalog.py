from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from pydantic import TypeAdapter

from app.data.poi_mapping import to_poi
from app.data.quality import DataWarning
from app.data.raw import RawPoi
from app.data.rules.coordinates import normalize_coordinates
from app.data.rules.duplicates import remove_duplicates
from app.domain.poi import Poi

_RAW_CATALOG = TypeAdapter(list[RawPoi])


@dataclass(frozen=True)
class Catalog:
    pois: tuple[Poi, ...]
    warnings: tuple[DataWarning, ...]

    def get(self, poi_id: str) -> Poi | None:
        return next((poi for poi in self.pois if poi.id == poi_id), None)


def load_catalog(path: Path) -> Catalog:
    raw_pois = _RAW_CATALOG.validate_json(path.read_bytes())
    _ensure_unique_ids(raw_pois)

    coordinates, warnings = normalize_coordinates({raw.id: (raw.lat, raw.lon) for raw in raw_pois})
    pois: list[Poi] = []
    for raw in raw_pois:
        poi, poi_warnings = to_poi(raw, coordinates[raw.id])
        pois.append(poi)
        warnings += poi_warnings

    unique_pois, duplicate_warnings = remove_duplicates(pois)
    return Catalog(pois=tuple(unique_pois), warnings=(*warnings, *duplicate_warnings))


def _ensure_unique_ids(raw_pois: list[RawPoi]) -> None:
    counts = Counter(raw.id for raw in raw_pois)
    repeated = sorted(poi_id for poi_id, count in counts.items() if count > 1)
    if repeated:
        raise ValueError(f"Repeated POI ids in the catalog: {repeated}")
