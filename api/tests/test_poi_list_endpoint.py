from typing import Any

from fastapi.testclient import TestClient

OPEN_ON_A_NOVEMBER_MONDAY_AT_NOON = [
    "poi-001",
    "poi-002",
    "poi-005",
    "poi-006",
    "poi-007",
    "poi-010",
    "poi-011",
    "poi-012",
    "poi-016",
    "poi-017",
]


def list_ids(client: TestClient, **params: str) -> list[str]:
    response = client.get("/pois", params=params)
    assert response.status_code == 200
    body: list[dict[str, Any]] = response.json()
    return [poi["id"] for poi in body]


def test_without_filters_returns_the_whole_catalog_without_the_duplicate(
    client: TestClient,
) -> None:
    ids = list_ids(client)

    assert len(ids) == 17
    assert "poi-004" not in ids


def test_filters_by_category(client: TestClient) -> None:
    assert list_ids(client, categoria="museo") == ["poi-003", "poi-013", "poi-015"]


def test_accessible_true_ignores_what_descriptions_claim(client: TestClient) -> None:
    ids = list_ids(client, accesible="true")

    assert "poi-013" not in ids
    assert "poi-011" not in ids
    assert "poi-003" in ids


def test_accessible_false_excludes_unknown_accessibility(client: TestClient) -> None:
    ids = list_ids(client, accesible="false")

    assert "poi-013" in ids
    assert "poi-011" not in ids


def test_open_on_monday_at_noon_matches_evaluation_q3(client: TestClient) -> None:
    ids = list_ids(client, abierto_en="1T12:00")

    assert ids == OPEN_ON_A_NOVEMBER_MONDAY_AT_NOON
    assert {"poi-001", "poi-006", "poi-010", "poi-002", "poi-005"} <= set(ids)
    assert not {"poi-003", "poi-015", "poi-008"} & set(ids)


def test_unknown_opening_hours_never_appear_as_open(client: TestClient) -> None:
    assert "poi-018" not in list_ids(client, abierto_en="1T12:00")


def test_seasonal_poi_depends_on_the_date(client: TestClient) -> None:
    assert "poi-014" not in list_ids(client, abierto_en="1T12:00")
    assert "poi-014" in list_ids(client, abierto_en="2026-07-06T12:00")


def test_filters_are_combined(client: TestClient) -> None:
    ids = list_ids(client, categoria="naturaleza", accesible="true", abierto_en="1T12:00")

    assert ids == ["poi-002", "poi-012"]


def test_texts_follow_the_requested_language(client: TestClient) -> None:
    body = client.get("/pois", params={"categoria": "museo", "idioma": "en"}).json()

    assert body[0]["nombre"] == {"texto": "Olive Oil Museum", "idioma": "en"}
    assert body[0]["descripcion"]["idioma"] == "en"
    assert body[0]["abierto_ahora"] is False
