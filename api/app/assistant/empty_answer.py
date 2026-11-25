from collections.abc import Sequence

from app.assistant import template_texts as texts
from app.assistant.answer import Answer
from app.assistant.interpretation.interpretation import Interpretation
from app.domain.localized_text import Language
from app.domain.opening_query import OpeningQuery
from app.domain.poi import Category, Poi

_WEEKDAYS = {
    Language.ES: ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"),
    Language.EN: ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
}


def empty_answer(
    interpretation: Interpretation, named: Sequence[Poi], language: Language
) -> Answer:
    """Why nothing was found, so "no place matches" is not mistaken for "I don't know" (D-049).

    `named` are the places the question names that the filters left out.
    """
    if not interpretation.has_filters:
        return Answer(text=texts.not_found(language), poi_ids=())
    wanted = _describe(interpretation, language)
    if named:
        names = _join([poi.name.resolve(language).text for poi in named], language)
        return Answer(text=_named_place_does_not_match(names, wanted, language), poi_ids=())
    return Answer(text=_no_place_matches(wanted, language), poi_ids=())


def _no_place_matches(wanted: str, language: Language) -> str:
    if language is Language.EN:
        return f"No place in the catalogue matches everything you asked for ({wanted})."
    return f"Ningún lugar del catálogo cumple todo lo que buscas ({wanted})."


def _named_place_does_not_match(names: str, wanted: str, language: Language) -> str:
    # "Does not list" rather than "is not": the catalogue may simply not know (accesible = null).
    if language is Language.EN:
        return f"The catalogue does not list {names} as matching what you asked for ({wanted})."
    return f"En el catálogo no consta que {names} cumpla lo que buscas ({wanted})."


def _describe(interpretation: Interpretation, language: Language) -> str:
    criteria = interpretation.criteria
    parts = []
    if criteria.categories:
        chosen = [texts.category(c, language) for c in Category if c in criteria.categories]
        parts.append(f" {'or' if language is Language.EN else 'o'} ".join(chosen))
    if criteria.accessible:
        parts.append(texts.accessibility(True, language))
    if criteria.open_at:
        parts.append(_open_at(criteria.open_at, language))
    return " · ".join(parts)


def _open_at(query: OpeningQuery, language: Language) -> str:
    day = _WEEKDAYS[language][query.weekday - 1]
    if language is Language.EN:
        at = f" at {query.at:%H:%M}" if query.at else ""
        return f"open on {day}{at}"
    at = f" a las {query.at:%H:%M}" if query.at else ""
    return f"abierto el {day}{at}"


def _join(names: list[str], language: Language) -> str:
    if len(names) == 1:
        return names[0]
    conjunction = "and" if language is Language.EN else "y"
    return f"{', '.join(names[:-1])} {conjunction} {names[-1]}"
