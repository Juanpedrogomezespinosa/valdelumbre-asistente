from app.domain.localized_text import Language
from app.domain.poi import Category
from app.domain.schedule import Season

_CATEGORY = {
    Language.ES: {
        Category.MONUMENT: "monumento",
        Category.MUSEUM: "museo",
        Category.NATURE: "naturaleza",
        Category.ROUTE: "ruta",
        Category.GASTRONOMY: "gastronomía",
        Category.SERVICE: "servicio",
        Category.PUBLIC_SPACE: "espacio público",
    },
    Language.EN: {
        Category.MONUMENT: "monument",
        Category.MUSEUM: "museum",
        Category.NATURE: "nature",
        Category.ROUTE: "route",
        Category.GASTRONOMY: "food and drink",
        Category.SERVICE: "service",
        Category.PUBLIC_SPACE: "public space",
    },
}
_ACCESSIBILITY = {
    Language.ES: {True: "accesible", False: "no accesible", None: "sin datos de accesibilidad"},
    Language.EN: {True: "accessible", False: "not accessible", None: "no accessibility data"},
}
_MONTHS = {
    Language.ES: (
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ),
    Language.EN: (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ),
}


def not_found(language: Language) -> str:
    if language is Language.EN:
        return "I don't have information about that in the Valdelumbre catalogue."
    return "No tengo información sobre eso en el catálogo de Valdelumbre."


def introduction(count: int, corrects_single_answer: bool, language: Language) -> str:
    if language is Language.EN:
        if corrects_single_answer:
            return (
                f"There isn't just one place: the catalogue has {count} "
                "that match what you are looking for:"
            )
        return f"I found {count} {'place' if count == 1 else 'places'} in the catalogue:"
    if corrects_single_answer:
        return f"No hay un único lugar: en el catálogo hay {count} que cumplen lo que buscas:"
    return f"He encontrado {count} {'lugar' if count == 1 else 'lugares'} en el catálogo:"


def category(value: Category, language: Language) -> str:
    return _CATEGORY[language][value]


def accessibility(value: bool | None, language: Language) -> str:
    return _ACCESSIBILITY[language][value]


def season(value: Season, language: Language) -> str:
    start, end = _day_and_month(value.start, language), _day_and_month(value.end, language)
    if language is Language.EN:
        return f"only from {start} to {end}"
    return f"solo del {start} al {end}"


def _day_and_month(month_day: tuple[int, int], language: Language) -> str:
    month, day = month_day
    month_name = _MONTHS[language][month - 1]
    return f"{day} {month_name}" if language is Language.EN else f"{day} de {month_name}"
