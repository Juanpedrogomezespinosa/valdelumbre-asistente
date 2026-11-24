import pytest

from app.domain.coordinates import Coordinates


def test_valid_coordinates_are_accepted() -> None:
    castle = Coordinates(lat=40.4172, lon=-3.7051)

    assert (castle.lat, castle.lon) == (40.4172, -3.7051)


@pytest.mark.parametrize(("lat", "lon"), [(90.1, 0.0), (-90.1, 0.0), (0.0, 180.1), (0.0, -180.1)])
def test_coordinates_outside_the_globe_are_rejected(lat: float, lon: float) -> None:
    with pytest.raises(ValueError, match="out of range"):
        Coordinates(lat=lat, lon=lon)
