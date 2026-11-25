from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.assistant.interpretation.interpretation import interpret
from app.assistant.retrieval import retrieve
from app.domain.localized_text import LocalizedText
from app.domain.poi import Category, Poi
from tests.poi_factory import make_poi

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=ZoneInfo("Europe/Madrid"))

CATALOG = [
    make_poi(
        "castle",
        name=LocalizedText(es="Castillo de Valdelumbre", en="Valdelumbre Castle"),
        tags=("historia", "vistas"),
    ),
    make_poi("park", category=Category.NATURE, accessible=True, tags=("familias", "naturaleza")),
    make_poi("winery", category=Category.GASTRONOMY, accessible=True, tags=("gastronomía", "vino")),
    make_poi("museum", category=Category.MUSEUM, accessible=True, tags=("familias", "naturaleza")),
    make_poi("viewpoint", category=Category.NATURE, tags=("vistas",)),
]


def retrieved(question: str) -> list[str]:
    return [poi.id for poi in retrieve(CATALOG, interpret(question, NOW))]


def test_a_topic_keeps_only_the_places_that_have_it() -> None:
    assert retrieved("¿Dónde puedo probar vino?") == ["winery"]


def test_tags_are_compared_without_accents() -> None:
    assert retrieved("Me interesa la gastronomía") == ["winery"]


def test_a_topic_can_match_the_category_code() -> None:
    assert retrieved("Me gusta la naturaleza") == ["park", "museum", "viewpoint"]


def test_filters_apply_before_topics() -> None:
    assert retrieved("Something to do with kids outdoors?") == ["park"]


def test_places_matching_more_topics_come_first() -> None:
    assert retrieved("Historia y vistas") == ["castle", "viewpoint"]


def test_a_keyword_can_match_a_place_name_in_either_language() -> None:
    assert retrieved("¿A qué hora abre el castillo?") == ["castle"]
    assert retrieved("Tell me about the castle") == ["castle"]


def test_only_filters_keep_every_candidate() -> None:
    assert retrieved("¿Qué es accesible?") == ["park", "winery", "museum"]


def test_keywords_that_match_no_name_are_ignored_when_there_are_filters() -> None:
    assert retrieved("Voy en silla de ruedas, ¿qué puedo visitar de museos?") == ["museum"]


def test_nothing_recognisable_retrieves_nothing() -> None:
    assert retrieved("¿Hay algún sitio de aventura con tirolina?") == []


def test_a_topic_no_place_has_retrieves_nothing() -> None:
    assert retrieved("Quiero ir de compras") == []


def test_never_returns_places_outside_the_catalog() -> None:
    results: list[Poi] = retrieve(CATALOG, interpret("Historia", NOW))

    assert all(poi in CATALOG for poi in results)


def test_a_named_place_that_fails_the_filters_is_not_replaced_by_others() -> None:
    catalog = [
        make_poi("castle", name=LocalizedText(es="Castillo"), accessible=False),
        make_poi("park", accessible=True),
    ]

    assert retrieve(catalog, interpret("¿Es accesible el castillo?", NOW)) == []


def test_a_word_shared_by_several_names_does_not_name_a_place() -> None:
    catalog = [
        make_poi("alameda", name=LocalizedText(es="Parque de la Alameda", en="Alameda Park")),
        make_poi("car-park", name=LocalizedText(es="Aparcamiento", en="Cuesta Car Park")),
    ]

    assert retrieve(catalog, interpret("Is there a zipline adventure park?", NOW)) == []
    assert retrieve(catalog, interpret("¿Dónde está el parque?", NOW)) == catalog[:1]


def test_a_named_place_wins_over_the_topic_its_name_suggests() -> None:
    # "Mirador" names the viewpoint but is also the topic "vistas", which the castle has:
    # asking about the viewpoint must not bring in the castle.
    catalog = [
        make_poi("castle", name=LocalizedText(es="Castillo"), tags=("vistas",)),
        make_poi("viewpoint", name=LocalizedText(es="Mirador del Alto"), tags=("vistas",)),
    ]

    found = retrieve(catalog, interpret("¿Dónde está el Mirador del Alto?", NOW))

    assert [poi.id for poi in found] == ["viewpoint"]


GENERIC_CATALOG = [
    make_poi("square", name=LocalizedText(es="Plaza Mayor", en="Main Square")),
    make_poi(
        "centre",
        name=LocalizedText(
            es="Centro de Interpretación del Valle", en="Valley Interpretation Centre"
        ),
        category=Category.MUSEUM,
    ),
    make_poi("office", name=LocalizedText(es="Oficina de Turismo", en="Tourist Office")),
    make_poi("tapestries", name=LocalizedText(es="Casa de los Tapices", en="Tapestry House")),
    make_poi("museum", name=LocalizedText(es="Museo del Aceite"), category=Category.MUSEUM),
]


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("What are the main attractions?", []),
        ("¿Qué museos hay en el centro del pueblo?", ["centre", "museum"]),
        ("I'm a tourist, which museums can I visit?", ["centre", "museum"]),
        ("Rutas por el valle", []),
        ("¿Dónde está la Plaza Mayor?", ["square"]),
        ("Main Square", ["square"]),
        ("¿Qué es el Centro de Interpretación?", ["centre"]),
        ("¿Abre la oficina de turismo?", ["office"]),
        ("Tapestry House", ["tapestries"]),
    ],
)
def test_a_common_word_in_a_name_needs_a_distinctive_one_beside_it(
    question: str, expected: list[str]
) -> None:
    found = retrieve(GENERIC_CATALOG, interpret(question, NOW))

    assert sorted(poi.id for poi in found) == sorted(expected)
