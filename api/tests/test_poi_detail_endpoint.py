import pytest
from fastapi.testclient import TestClient


def test_returns_the_poi_in_spanish_by_default(client: TestClient) -> None:
    response = client.get("/pois/poi-003")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "poi-003"
    assert body["nombre"] == {"texto": "Museo del Aceite", "idioma": "es"}
    assert body["categoria"] == "museo"
    assert body["accesible"] is True
    assert body["precio"]["texto"] == "Gratis"


def test_returns_the_poi_in_english_when_asked(client: TestClient) -> None:
    body = client.get("/pois/poi-003", params={"idioma": "en"}).json()

    assert body["nombre"] == {"texto": "Olive Oil Museum", "idioma": "en"}
    assert body["precio"]["texto"] == "Free"


@pytest.mark.parametrize(
    ("poi_id", "expected"),
    [("poi-001", True), ("poi-003", False), ("poi-014", False), ("poi-018", None)],
)
def test_open_now_uses_the_injected_clock(
    client: TestClient, poi_id: str, expected: bool | None
) -> None:
    body = client.get(f"/pois/{poi_id}").json()

    assert body["abierto_ahora"] is expected


def test_serves_corrected_data(client: TestClient) -> None:
    roman_bridge = client.get("/pois/poi-011").json()
    tapestry_house = client.get("/pois/poi-013").json()

    assert roman_bridge["coordenadas"] == {"lat": 40.421, "lon": -3.711}
    assert roman_bridge["accesible"] is None
    assert tapestry_house["descripcion"]["texto"] == "Colección de tapices flamencos."


def test_schedule_includes_slots_and_seasons(client: TestClient) -> None:
    schedule = client.get("/pois/poi-014").json()["horario"]

    assert schedule["conocido"] is True
    assert schedule["franjas"] == [
        {
            "dias": [1, 2, 3, 4, 5, 6, 7],
            "abre": "11:00",
            "cierra": "20:00",
            "temporada": {"desde": "06-01", "hasta": "09-30"},
        }
    ]


@pytest.mark.parametrize("poi_id", ["poi-999", "poi-004"])
def test_unknown_or_removed_poi_is_not_found(client: TestClient, poi_id: str) -> None:
    response = client.get(f"/pois/{poi_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"No existe ningún punto con id {poi_id}"}


def test_not_found_message_follows_the_requested_language(client: TestClient) -> None:
    response = client.get("/pois/poi-999", params={"idioma": "en"})

    assert response.json() == {"detail": "There is no point of interest with id poi-999"}
