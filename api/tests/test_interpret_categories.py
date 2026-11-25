import pytest

from app.assistant.interpretation.categories import categories_in
from app.domain.poi import Category
from app.domain.text_folding import fold

OUTDOORS = {Category.NATURE, Category.ROUTE, Category.PUBLIC_SPACE}


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("¿Qué puedo visitar de museos?", {Category.MUSEUM}),
        ("Is there a museum?", {Category.MUSEUM}),
        ("Monumentos del pueblo", {Category.MONUMENT}),
        ("¿Hay alguna ruta o sendero?", {Category.ROUTE}),
        ("Any hiking trails?", {Category.ROUTE}),
        ("¿Dónde puedo comer?", {Category.GASTRONOMY}),
        ("A good restaurant, please", {Category.GASTRONOMY}),
        ("Something to do with kids outdoors?", OUTDOORS),
        ("Planes al aire libre", OUTDOORS),
        ("Museos y monumentos", {Category.MUSEUM, Category.MONUMENT}),
    ],
)
def test_maps_words_to_categories(question: str, expected: set[Category]) -> None:
    assert categories_in(fold(question)) == expected


def test_no_category_words_means_no_category() -> None:
    assert categories_in(fold("¿Hay algún sitio de aventura con tirolina?")) == frozenset()
