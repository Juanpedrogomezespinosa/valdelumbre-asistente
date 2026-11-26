import re

from app.assistant.interpretation.phrases import contains_any

ACCESSIBILITY_PHRASES = (
    "accesible",
    "accesibles",
    "accesibilidad",
    "silla de ruedas",
    "sillas de ruedas",
    "movilidad reducida",
    "accessible",
    "accessibility",
    "wheelchair",
    "wheelchairs",
    "reduced mobility",
    "inaccessible",
)
UNKNOWN_ACCESSIBILITY_PHRASES = (
    "sin datos de accesibilidad",
    "no tienen datos de accesibilidad",
    "no tiene datos de accesibilidad",
    "accesibilidad desconocida",
    "no consta",
    "no accessibility data",
    "unknown accessibility",
    "accessibility unknown",
)
# "no son accesibles", "not wheelchair accessible": the negation sits just before the word.
_NEGATED = re.compile(
    r"\b(no|not|isn.?t|aren.?t)\s+(\w+\s+){0,2}(accesibles?|accessible)\b|\binaccessible\b"
)


def accessibility_in(folded: str) -> tuple[bool | None, bool]:
    """(wanted accessibility, whether it asks for places with unknown accessibility)."""
    if contains_any(folded, UNKNOWN_ACCESSIBILITY_PHRASES):
        return None, True
    if _NEGATED.search(folded):
        return False, False
    return (True if contains_any(folded, ACCESSIBILITY_PHRASES) else None), False
