"""Every kind of question the catalogue's fields can answer (H14), with the real catalogue.

The clock is fixed on Monday 23 November 2026 at 12:00 in Madrid (conftest).
"""

import pytest
from fastapi.testclient import TestClient

OPEN_MONDAY_NOON = {
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
}
# poi-018 has unknown hours: neither open nor closed (D-009).
CLOSED_MONDAY_NOON = {"poi-003", "poi-008", "poi-009", "poi-013", "poi-014", "poi-015"}
MUSEUMS = {"poi-003", "poi-013", "poi-015"}
NOT_ACCESSIBLE = {"poi-001", "poi-006", "poi-007", "poi-013", "poi-014", "poi-018"}
FREE = {
    "poi-002",
    "poi-003",
    "poi-005",
    "poi-007",
    "poi-010",
    "poi-011",
    "poi-012",
    "poi-014",
    "poi-015",
    "poi-017",
    "poi-018",
}
SERVICES = {"poi-010", "poi-016", "poi-017"}


def ask(client: TestClient, question: str, language: str = "es") -> dict[str, object]:
    body: dict[str, object] = client.post(
        "/preguntar", json={"pregunta": question, "idioma": language}
    ).json()
    return body


def cited(client: TestClient, question: str, language: str = "es") -> set[str]:
    ids = ask(client, question, language)["ids"]
    assert isinstance(ids, list)
    return set(ids)


@pytest.mark.parametrize(
    ("question", "language"),
    [
        ("que hay cerrado ahora mismo?", "es"),
        ("¿Qué está cerrado?", "es"),
        ("What is closed now?", "en"),
        ("¿Qué no está abierto ahora?", "es"),
    ],
)
def test_closed_means_closed_not_open(client: TestClient, question: str, language: str) -> None:
    assert cited(client, question, language) == CLOSED_MONDAY_NOON


def test_closed_on_a_day_with_a_category(client: TestClient) -> None:
    # The three museums close on Mondays.
    assert cited(client, "¿Qué museos están cerrados el lunes?") == MUSEUMS


def test_not_accessible_means_not_accessible(client: TestClient) -> None:
    assert cited(client, "¿Qué sitios no son accesibles?") == NOT_ACCESSIBLE
    assert cited(client, "Which places are not accessible?", "en") == NOT_ACCESSIBLE


def test_unknown_accessibility_is_its_own_answer(client: TestClient) -> None:
    assert cited(client, "¿Qué lugares no tienen datos de accesibilidad?") == {"poi-011"}


@pytest.mark.parametrize(
    ("question", "language"),
    [
        ("¿Qué es gratis?", "es"),
        ("¿Qué cosas son gratuitas?", "es"),
        ("Free places", "en"),
    ],
)
def test_free_places(client: TestClient, question: str, language: str) -> None:
    assert cited(client, question, language) == FREE


def test_things_to_do_without_spending_leave_out_services(client: TestClient) -> None:
    assert cited(client, "que puedo hacer sin gastar dinero?") == FREE - SERVICES
    assert cited(client, "Free things to do", "en") == FREE - SERVICES


def test_under_a_price_filters_by_price_and_names_no_car_park(client: TestClient) -> None:
    under_five = FREE | {"poi-001", "poi-006", "poi-013"}

    assert cited(client, "¿Qué cuesta menos de 5 euros?") == under_five
    assert cited(client, "Places under 5 €", "en") == under_five


def test_the_cheapest_paid_or_free_place(client: TestClient) -> None:
    assert cited(client, "¿Qué es lo más barato?") == FREE
    assert cited(client, "¿Cuál es el museo más barato?") == {"poi-003", "poi-015"}


def test_asking_the_hours_gives_each_place_its_hours(client: TestClient) -> None:
    lines = str(ask(client, "Dame el horario de todos los museos")["respuesta"]).splitlines()

    assert lines[1:] == [
        "- Museo del Aceite (museo · accesible · gratis) · horario: de martes a domingo "
        "de 10:00 a 18:00",
        "- Casa de los Tapices (museo · no accesible · 3 €) · horario: sábado y domingo "
        "de 11:00 a 14:00",
        "- Centro de Interpretación del Valle (museo · accesible · gratis) · horario: "
        "de martes a domingo de 10:00 a 14:00",
    ]


@pytest.mark.parametrize(
    ("question", "language", "expected"),
    [
        ("¿A qué hora abre el castillo?", "es", "horario: "),
        ("What are the opening hours of the castle?", "en", "hours: "),
        ("¿Qué horario tiene la ermita?", "es", "horario sin datos"),
        ("Opening times of the natural pool", "en", "only from 1 June to 30 September"),
    ],
)
def test_hours_of_one_place(
    client: TestClient, question: str, language: str, expected: str
) -> None:
    answer = ask(client, question, language)

    assert len(answer["ids"]) == 1  # type: ignore[arg-type]
    assert expected in str(answer["respuesta"])


def test_asking_what_opens_on_a_day_is_a_filter_not_an_hours_question(client: TestClient) -> None:
    assert "horario" not in str(ask(client, "¿Qué abre los domingos?")["respuesta"])


@pytest.mark.parametrize(
    "question", ["¿Qué puedo visitar?", "¿Qué hay que ver en Valdelumbre?", "What to see?"]
)
def test_what_to_see_lists_the_sights(client: TestClient, question: str) -> None:
    sights = cited(client, question, "en" if question.startswith("What") else "es")

    assert sights
    assert not sights & SERVICES
    assert not sights & {"poi-008", "poi-009"}


@pytest.mark.parametrize(
    ("question", "language"),
    [("¿Dónde aparco?", "es"), ("¿Hay parking?", "es"), ("Is there a car park?", "en")],
)
def test_parking_finds_the_car_park(client: TestClient, question: str, language: str) -> None:
    assert cited(client, question, language) == {"poi-017"}


def test_tonight_is_checked_at_night(client: TestClient) -> None:
    # Monday 21:00: the restaurant and the winery do not open on Mondays.
    assert cited(client, "restaurantes abiertos esta noche") == set()
    assert cited(client, "¿Qué está abierto esta noche?") == {
        "poi-002",
        "poi-005",
        "poi-007",
        "poi-011",
        "poi-012",
        "poi-016",
        "poi-017",
    }


def test_tomorrow_morning_is_tuesday_morning(client: TestClient) -> None:
    tuesday_morning = cited(client, "¿Qué hay abierto mañana por la mañana?")

    assert MUSEUMS - {"poi-013"} <= tuesday_morning
    assert "poi-013" not in tuesday_morning


@pytest.mark.parametrize(
    ("question", "language"), [("Is there free wifi?", "en"), ("¿Hay wifi gratis?", "es")]
)
def test_free_wifi_is_about_wifi_not_about_price(
    client: TestClient, question: str, language: str
) -> None:
    assert cited(client, question, language) == set()
