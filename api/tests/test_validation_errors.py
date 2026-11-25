import pytest
from fastapi.testclient import TestClient


def detail(client: TestClient, path: str, **params: str) -> str:
    response = client.get(path, params=params)
    assert response.status_code == 422
    message: str = response.json()["detail"]
    return message


def test_unknown_category_lists_the_valid_ones_in_spanish(client: TestClient) -> None:
    assert detail(client, "/pois", categoria="playa") == (
        "El parámetro «categoria» no es válido. Valores posibles: monumento, museo, "
        "naturaleza, ruta, gastronomia, servicio, espacio_publico."
    )


def test_message_follows_the_requested_language(client: TestClient) -> None:
    assert detail(client, "/pois", accesible="quizas", idioma="en") == (
        "The «accesible» parameter is not valid. Allowed values: true, false."
    )


@pytest.mark.parametrize("path", ["/pois", "/pois/poi-001"])
def test_an_unreadable_language_falls_back_to_spanish(client: TestClient, path: str) -> None:
    assert detail(client, path, idioma="fr") == (
        "El parámetro «idioma» no es válido. Valores posibles: es, en."
    )


@pytest.mark.parametrize(("language", "start"), [("es", "El parámetro"), ("en", "The «")])
def test_invalid_open_at_explains_the_format(client: TestClient, language: str, start: str) -> None:
    message = detail(client, "/pois", abierto_en="lunes", idioma=language)

    assert message.startswith(start)
    assert "abierto_en" in message
    assert "1T12:00" in message
    assert "2026-07-06T12:00" in message
