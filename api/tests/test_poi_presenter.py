from datetime import datetime

from app.domain.localized_text import Language, LocalizedText
from app.domain.poi import Category, Poi
from app.domain.price import Price
from app.domain.schedule import Schedule
from app.routes.presenters.poi import present_poi

UNTRANSLATED_DESCRIPTION = Poi(
    id="poi-x",
    name=LocalizedText(es="Plaza Mayor", en="Main Square"),
    category=Category.PUBLIC_SPACE,
    description=LocalizedText(es="Plaza porticada.", en=None),
    coordinates=None,
    accessible=True,
    schedule=Schedule(always_open=True, slots=()),
    price=Price.free(),
    tags=(),
)


def test_each_text_reports_the_language_it_is_actually_served_in() -> None:
    response = present_poi(UNTRANSLATED_DESCRIPTION, Language.EN, datetime(2026, 11, 23, 12, 0))

    assert (response.nombre.texto, response.nombre.idioma) == ("Main Square", Language.EN)
    assert (response.descripcion.texto, response.descripcion.idioma) == (
        "Plaza porticada.",
        Language.ES,
    )
