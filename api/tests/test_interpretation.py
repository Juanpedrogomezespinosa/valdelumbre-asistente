from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from app.assistant.interpretation.interpretation import interpret
from app.domain.opening_query import OpeningQuery
from app.domain.poi import Category

NOW = datetime(2026, 11, 25, 10, 20, tzinfo=ZoneInfo("Europe/Madrid"))


def test_q1_wheelchair_and_museums() -> None:
    result = interpret("Voy en silla de ruedas, ¿qué puedo visitar de museos?", NOW)

    assert result.criteria.accessible is True
    assert result.criteria.categories == {Category.MUSEUM}
    assert result.topics == frozenset()


def test_q2_kids_outdoors_in_english() -> None:
    result = interpret("Something to do with kids outdoors?", NOW)

    assert result.criteria.categories == {Category.NATURE, Category.ROUTE, Category.PUBLIC_SPACE}
    assert result.topics == {"familias"}


def test_q3_open_on_monday_at_noon() -> None:
    result = interpret("¿Qué está abierto un lunes a las 12:00?", NOW)

    assert result.criteria.open_at == OpeningQuery(
        weekday=1, at=time(12, 0), reference_date=date(2026, 11, 25)
    )


def test_q4_local_wine() -> None:
    assert interpret("¿Dónde puedo probar vino de la zona?", NOW).topics == {"vino"}


def test_q5_only_accessible_place_flags_the_premise() -> None:
    result = interpret("¿Cuál es el único sitio accesible del pueblo?", NOW)

    assert result.criteria.accessible is True
    assert result.asks_for_only_one is True


def test_q6_zipline_has_no_recognised_signal() -> None:
    result = interpret("¿Hay algún sitio de aventura con tirolina?", NOW)

    assert not result.has_filters
    assert result.topics == frozenset()
    assert "tirolina" in result.keywords


def test_keywords_leave_out_words_already_interpreted_and_short_words() -> None:
    result = interpret("¿A qué hora abre el castillo los lunes? Voy con niños", NOW)

    assert "castillo" in result.keywords
    assert not {"lunes", "ninos", "abre", "hora", "con", "voy"} & result.keywords


def test_keywords_leave_out_the_village_name() -> None:
    assert "valdelumbre" not in interpret("¿Qué ver en Valdelumbre?", NOW).keywords


def test_without_signals_no_accessibility_or_time_filter_is_applied() -> None:
    result = interpret("¿Dónde puedo probar vino de la zona?", NOW)

    assert result.criteria.accessible is None
    assert result.criteria.open_at is None
    assert result.criteria.categories is None


def test_asking_the_price_does_not_name_the_cuesta_car_park() -> None:
    # "cuesta" (costs) is also a word of "Aparcamiento de la Cuesta".
    result = interpret("¿Cuánto cuesta el castillo?", NOW)

    assert "cuesta" not in result.keywords
    assert "castillo" in result.keywords


def test_cuesta_still_names_the_car_park_when_no_price_is_asked() -> None:
    assert "cuesta" in interpret("Tell me about Cuesta Car Park", NOW).keywords
