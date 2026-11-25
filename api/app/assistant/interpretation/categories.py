from app.assistant.interpretation.phrases import contains_any
from app.domain.poi import Category


def _each(phrases: tuple[str, ...], *categories: Category) -> dict[str, frozenset[Category]]:
    return dict.fromkeys(phrases, frozenset(categories))


# Only words that name a kind of place filter by category. Softer themes such as
# "naturaleza" are topics instead, so they rank places rather than exclude them.
CATEGORY_PHRASES: dict[str, frozenset[Category]] = {
    **_each(("museo", "museos", "museum", "museums"), Category.MUSEUM),
    **_each(("monumento", "monumentos", "monument", "monuments"), Category.MONUMENT),
    **_each(
        ("ruta", "rutas", "sendero", "senderos", "route", "routes", "trail", "trails"),
        Category.ROUTE,
    ),
    **_each(
        (
            "comer",
            "come",
            "comen",
            "comemos",
            "comida",
            "cenar",
            "cena",
            "almorzar",
            "almuerzo",
            "restaurante",
            "restaurantes",
            "eat",
            "dine",
            "dinner",
            "lunch",
            "food",
            "restaurant",
            "restaurants",
        ),
        Category.GASTRONOMY,
    ),
    **_each(
        ("al aire libre", "aire libre", "outdoors", "outdoor", "outside"),
        Category.NATURE,
        Category.ROUTE,
        Category.PUBLIC_SPACE,
    ),
}


def categories_in(folded: str) -> frozenset[Category]:
    found = (
        categories
        for phrase, categories in CATEGORY_PHRASES.items()
        if contains_any(folded, (phrase,))
    )
    return frozenset[Category]().union(*found)
