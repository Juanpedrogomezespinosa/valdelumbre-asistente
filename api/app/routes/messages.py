from collections.abc import Iterable

from app.domain.localized_text import Language


def poi_not_found(poi_id: str, language: Language) -> str:
    if language is Language.EN:
        return f"There is no point of interest with id {poi_id}"
    return f"No existe ningún punto con id {poi_id}"


def invalid_parameter(name: str, allowed: Iterable[str], language: Language) -> str:
    values = ", ".join(allowed)
    if language is Language.EN:
        message = f"The «{name}» parameter is not valid."
        return f"{message} Allowed values: {values}." if values else message
    message = f"El parámetro «{name}» no es válido."
    return f"{message} Valores posibles: {values}." if values else message


def invalid_open_at(language: Language) -> str:
    if language is Language.EN:
        return (
            "The «abierto_en» parameter is not valid. Use an ISO weekday (1 = Monday) and "
            "a time, such as 1T12:00, or a full date and time, such as 2026-07-06T12:00."
        )
    return (
        "El parámetro «abierto_en» no es válido. Usa un día ISO (1 = lunes) y una hora, "
        "como 1T12:00, o una fecha y hora completas, como 2026-07-06T12:00."
    )
