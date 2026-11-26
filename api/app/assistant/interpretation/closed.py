from app.assistant.interpretation.phrases import contains_any

CLOSED_PHRASES = (
    "cerrado",
    "cerrados",
    "cerrada",
    "cerradas",
    "no esta abierto",
    "no estan abiertos",
    "no esta abierta",
    "no estan abiertas",
    "closed",
    "not open",
)


def asks_closed(folded: str) -> bool:
    return contains_any(folded, CLOSED_PHRASES)
