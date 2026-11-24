from collections.abc import Mapping
from statistics import median

from app.data.quality import DataWarning, WarningKind
from app.domain.coordinates import Coordinates

RawCoordinates = tuple[float, float]

# About 100 km: far beyond the extent of a village, far below the jump of a lat/lon swap.
_MAX_DEGREES_FROM_CATALOG_CENTRE = 1.0


def normalize_coordinates(
    raw: Mapping[str, RawCoordinates],
) -> tuple[dict[str, Coordinates | None], list[DataWarning]]:
    """Validate each point against the catalog median, which a single wrong point cannot drag."""
    if not raw:
        return {}, []
    centre = (
        median(lat for lat, _ in raw.values()),
        median(lon for _, lon in raw.values()),
    )
    coordinates: dict[str, Coordinates | None] = {}
    warnings: list[DataWarning] = []
    for poi_id, (lat, lon) in raw.items():
        if _is_near(centre, lat, lon):
            coordinates[poi_id] = Coordinates(lat=lat, lon=lon)
        elif _is_near(centre, lat=lon, lon=lat):
            coordinates[poi_id] = Coordinates(lat=lon, lon=lat)
            warnings.append(
                DataWarning(
                    poi_id,
                    WarningKind.SWAPPED_COORDINATES,
                    detail=f"Latitude and longitude swapped: ({lat}, {lon})",
                    action=f"Swapped back to ({lon}, {lat})",
                )
            )
        else:
            coordinates[poi_id] = None
            warnings.append(
                DataWarning(
                    poi_id,
                    WarningKind.OUTLIER_COORDINATES,
                    detail=f"Coordinates far from the rest of the catalog: ({lat}, {lon})",
                    action="Served without coordinates (hidden from the map)",
                )
            )
    return coordinates, warnings


def _is_near(centre: RawCoordinates, lat: float, lon: float) -> bool:
    centre_lat, centre_lon = centre
    return (
        abs(lat - centre_lat) <= _MAX_DEGREES_FROM_CATALOG_CENTRE
        and abs(lon - centre_lon) <= _MAX_DEGREES_FROM_CATALOG_CENTRE
    )
