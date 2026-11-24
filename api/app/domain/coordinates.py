from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not (-90 <= self.lat <= 90 and -180 <= self.lon <= 180):
            raise ValueError(f"Coordinates out of range: {self.lat}, {self.lon}")
