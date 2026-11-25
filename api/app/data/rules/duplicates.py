from collections.abc import Sequence

from app.data.quality import DataWarning, WarningKind
from app.domain.poi import Poi
from app.domain.text_folding import fold

# Four decimals is about 11 m: two records closer than that describe the same place.
_SAME_PLACE_DECIMALS = 4


def remove_duplicates(pois: Sequence[Poi]) -> tuple[list[Poi], list[DataWarning]]:
    """Merge records with the same place and name, keeping the most complete one (D-007)."""
    best_by_key: dict[tuple[str, float, float], Poi] = {}
    for poi in pois:
        key = _duplicate_key(poi)
        if key is None:
            continue
        current = best_by_key.get(key)
        if current is None or _completeness(poi) > _completeness(current):
            best_by_key[key] = poi

    kept: list[Poi] = []
    warnings: list[DataWarning] = []
    for poi in pois:
        key = _duplicate_key(poi)
        best = poi if key is None else best_by_key[key]
        if best is poi:
            kept.append(poi)
        else:
            warnings.append(
                DataWarning(
                    poi.id,
                    WarningKind.DUPLICATE_POI,
                    detail=f"Same place and name as {best.id}",
                    action=f"Removed; {best.id} kept as the more complete record",
                )
            )
    return kept, warnings


def _duplicate_key(poi: Poi) -> tuple[str, float, float] | None:
    if poi.coordinates is None:
        return None
    return (
        fold(poi.name.es),
        round(poi.coordinates.lat, _SAME_PLACE_DECIMALS),
        round(poi.coordinates.lon, _SAME_PLACE_DECIMALS),
    )


def _completeness(poi: Poi) -> int:
    return sum(
        (
            poi.name.en is not None,
            poi.description.en is not None,
            poi.accessible is not None,
            poi.schedule.is_known,
            not poi.price.is_unknown,
            bool(poi.tags),
        )
    )
