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
)


def wants_accessible(folded: str) -> bool:
    return contains_any(folded, ACCESSIBILITY_PHRASES)
