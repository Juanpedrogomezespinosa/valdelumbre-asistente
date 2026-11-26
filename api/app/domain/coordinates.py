import math
from dataclasses import dataclass

_METRES_PER_DEGREE_LAT = 111_320


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not (-90 <= self.lat <= 90 and -180 <= self.lon <= 180):
            raise ValueError(f"Coordinates out of range: {self.lat}, {self.lon}")

    def metres_to(self, other: "Coordinates") -> float:
        """Straight-line distance. A flat approximation: at village scale the error is
        negligible, and it matches the web's map (web/src/app/pois/map-geometry.ts)."""
        metres_per_degree_lon = _METRES_PER_DEGREE_LAT * math.cos(math.radians(self.lat))
        north = (other.lat - self.lat) * _METRES_PER_DEGREE_LAT
        east = (other.lon - self.lon) * metres_per_degree_lon
        return math.hypot(north, east)
