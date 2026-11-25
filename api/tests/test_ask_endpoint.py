from typing import Any

import pytest
from fastapi.testclient import TestClient


def ask(client: TestClient, body: Any) -> Any:
    return client.post("/preguntar", json=body)


def test_returns_exactly_an_answer_and_the_cited_ids(client: TestClient) -> None:
    response = ask(
        client,
        {"pregunta": "Voy en silla de ruedas, ¿qué puedo visitar de museos?", "idioma": "es"},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"respuesta", "ids"}
    assert body["ids"] == ["poi-003", "poi-015"]
    assert body["respuesta"].startswith("He encontrado 2 lugares")


def test_answers_in_the_requested_language(client: TestClient) -> None:
    body = ask(client, {"pregunta": "Something to do with kids outdoors?", "idioma": "en"}).json()

    assert body["ids"] == ["poi-007", "poi-012"]
    assert body["respuesta"].startswith("I found 2 places")


def test_language_defaults_to_spanish(client: TestClient) -> None:
    body = ask(client, {"pregunta": "¿Dónde puedo probar vino de la zona?"}).json()

    assert body == {
        "respuesta": "He encontrado 1 lugar en el catálogo:\n"
        "- Bodega La Encina (gastronomía · accesible · 15 €)",
        "ids": ["poi-008"],
    }


def test_a_question_outside_the_catalog_cites_nothing(client: TestClient) -> None:
    body = ask(client, {"pregunta": "¿Hay algún sitio de aventura con tirolina?"}).json()

    assert body == {
        "respuesta": "No tengo información sobre eso en el catálogo de Valdelumbre. Puedes "
        "preguntarme por tipo de lugar (museos, monumentos, rutas, dónde comer), accesibilidad, "
        "día y hora, o temas como vino, niños o vistas.",
        "ids": [],
    }


def test_an_understood_question_without_matches_says_so(client: TestClient) -> None:
    # The catalogue has no accessible monument: an empty answer, but not "no information".
    body = ask(client, {"pregunta": "Quiero ver monumentos que sean accesibles"}).json()

    assert body == {
        "respuesta": "Ningún lugar del catálogo cumple todo lo que buscas (monumento · accesible).",
        "ids": [],
    }


def test_a_named_place_that_does_not_match_is_named_in_the_answer(client: TestClient) -> None:
    body = ask(client, {"pregunta": "¿Es accesible el castillo?"}).json()

    assert body["respuesta"] == (
        "En el catálogo no consta que Castillo de Valdelumbre cumpla lo que buscas (accesible)."
    )
    assert body["ids"] == []


def test_uses_the_injected_clock(client: TestClient) -> None:
    # The test clock is a November Monday at noon: the natural pool is out of season.
    body = ask(client, {"pregunta": "¿Qué está abierto ahora?"}).json()

    assert "poi-001" in body["ids"]
    assert "poi-014" not in body["ids"]


def error(client: TestClient, body: Any) -> str:
    response = ask(client, body)
    assert response.status_code == 422
    message: str = response.json()["detail"]
    return message


@pytest.mark.parametrize("question", ["", "   ", "x" * 501])
def test_an_empty_or_too_long_question_is_rejected(client: TestClient, question: str) -> None:
    assert error(client, {"pregunta": question, "idioma": "es"}) == (
        "La pregunta no puede estar vacía ni superar los 500 caracteres."
    )


def test_the_error_follows_the_language_in_the_body(client: TestClient) -> None:
    assert error(client, {"pregunta": "", "idioma": "en"}) == (
        "The question cannot be empty or longer than 500 characters."
    )


def test_an_invalid_language_in_the_body_is_reported_in_spanish(client: TestClient) -> None:
    assert error(client, {"pregunta": "Hola", "idioma": "fr"}) == (
        "El parámetro «idioma» no es válido. Valores posibles: es, en."
    )


@pytest.mark.parametrize("body", [None, {"idioma": "es"}, ["pregunta"]])
def test_a_malformed_body_explains_the_expected_shape(client: TestClient, body: Any) -> None:
    assert error(client, body).startswith("La petición debe ser un JSON")


def test_invalid_json_explains_the_expected_shape(client: TestClient) -> None:
    response = client.post(
        "/preguntar", content=b"{pregunta", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422
    assert response.json()["detail"].startswith("La petición debe ser un JSON")


def test_says_it_cannot_answer_about_what_it_does_not_look_up(client: TestClient) -> None:
    body = ask(client, {"pregunta": "hay wifi en el parque?"}).json()

    assert body["respuesta"].splitlines() == [
        "No puedo responder sobre wifi: no es un dato que yo consulte. Mira la ficha del lugar "
        "o pregunta en la Oficina de Turismo. Esto es lo que sí sé:",
        "- Parque de la Alameda (naturaleza · accesible · gratis)",
    ]
    assert body["ids"] == ["poi-012"]


def test_with_nothing_else_to_say_it_only_explains_what_it_cannot_answer(
    client: TestClient,
) -> None:
    body = ask(client, {"pregunta": "Do you allow dogs?", "idioma": "en"}).json()

    assert body == {
        "respuesta": "I can't answer about pets: it is not something I look up. Check each "
        "place's page or ask at the Tourist Office.",
        "ids": [],
    }


def test_asking_what_a_place_costs_answers_with_that_place_and_its_price(
    client: TestClient,
) -> None:
    body = ask(client, {"pregunta": "¿Cuánto cuesta el castillo?"}).json()

    assert body["ids"] == ["poi-001"]
    assert "4,50 €" in body["respuesta"]
