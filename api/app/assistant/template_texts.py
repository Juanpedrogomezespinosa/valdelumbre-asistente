from app.domain.localized_text import Language
from app.domain.poi import Category
from app.domain.price import Price
from app.domain.price_text import price_text
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
_AND = {Language.ES: "y", Language.EN: "and"}
_WEEKDAYS = {
    Language.ES: ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"),
    Language.EN: ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
}
_UNRECORDED = {
    Language.ES: {
        "wifi": "wifi",
        "mascotas": "mascotas",
        "aseos": "aseos",
        "pago": "formas de pago",
        "reservas": "reservas",
        "visitas_guiadas": "visitas guiadas",
        "terraza": "terrazas",
        "cajero": "cajeros",
        "dietas": "menús especiales (vegano, sin gluten…)",
    },
    Language.EN: {
        "wifi": "wifi",
        "mascotas": "pets",
        "aseos": "toilets",
        "pago": "payment methods",
        "reservas": "bookings",
        "visitas_guiadas": "guided tours",
        "terraza": "terraces",
        "cajero": "cash machines",
        "dietas": "special diets (vegan, gluten-free…)",
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


def not_found(language: Language, referral: str | None) -> str:
    # Says what can be asked, so a question outside the vocabulary is not a dead end.
    if language is Language.EN:
        text = (
            "I don't have information about that in the Valdelumbre catalogue. You can ask me "
            "about kinds of places (museums, monuments, trails, where to eat), accessibility, "
            "day and time, or themes such as wine, kids or views."
        )
        return f"{text} For anything else, {referral}." if referral else text
    text = (
        "No tengo información sobre eso en el catálogo de Valdelumbre. Puedes preguntarme por "
        "tipo de lugar (museos, monumentos, rutas, dónde comer), accesibilidad, día y hora, o "
        "temas como vino, niños o vistas."
    )
    return f"{text} Para todo lo demás, {referral}." if referral else text


def cannot_answer(subjects: frozenset[str], language: Language, referral: str | None) -> str:
    """For what the assistant does not look up (D-050): say so instead of implying a yes."""
    order = [subject for subject in _UNRECORDED[language] if subject in subjects]
    joined = join([_UNRECORDED[language][subject] for subject in order], language)
    if language is Language.EN:
        where = f" or {referral}" if referral else ""
        return (
            f"I can't answer about {joined}: it is not something I look up. "
            f"Check each place's page{where}."
        )
    where = f" o {referral}" if referral else ""
    return (
        f"No puedo responder sobre {joined}: no es un dato que yo consulte. "
        f"Mira la ficha del lugar{where}."
    )


def join(items: list[str], language: Language) -> str:
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} {_AND[language]} {items[-1]}"


def weekday(iso_weekday: int, language: Language) -> str:
    return _WEEKDAYS[language][iso_weekday - 1]


def what_i_know(language: Language) -> str:
    return "This is what I do know:" if language is Language.EN else "Esto es lo que sí sé:"


def price(value: Price, language: Language) -> str:
    if value.min_eur is None:
        return "no price data" if language is Language.EN else "precio sin datos"
    return price_text(value, language).lower() if value.is_free else price_text(value, language)


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
