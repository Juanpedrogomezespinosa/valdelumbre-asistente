from collections.abc import Sequence

from app.assistant.opening_hours_text import opening_hours
from app.domain.localized_text import Language
from app.domain.poi import Poi
from app.domain.text_folding import fold

_OFFICE_NAMES = ("oficina de turismo", "tourist office")


def find_tourist_office(pois: Sequence[Poi]) -> Poi | None:
    """Found by name rather than by id, so another catalogue with an office works the same."""
    return next((poi for poi in pois if _is_tourist_office(poi)), None)


def referral(office: Poi | None, language: Language) -> str | None:
    """Where to ask what the catalogue cannot answer, with the office's hours when simple."""
    if office is None:
        return None
    name = office.name.resolve(language).text
    hours = opening_hours(office.schedule, language)
    where = f"ask at the {name}" if language is Language.EN else f"pregunta en la {name}"
    return f"{where} ({hours})" if hours else where


def _is_tourist_office(poi: Poi) -> bool:
    names = [poi.name.es, poi.name.en or ""]
    return any(office in fold(name) for name in names for office in _OFFICE_NAMES)
