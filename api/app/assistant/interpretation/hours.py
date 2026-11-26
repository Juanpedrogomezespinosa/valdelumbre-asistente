from app.assistant.interpretation.phrases import contains_any

HOURS_PHRASES = (
    "horario",
    "horarios",
    "a que hora",
    "a que horas",
    "cuando abre",
    "cuando abren",
    "cuando cierra",
    "cuando cierran",
    "hora de apertura",
    "hora de cierre",
    "opening hours",
    "opening times",
    "what time",
    "when does",
    "when do",
)


def asks_hours(folded: str) -> bool:
    return contains_any(folded, HOURS_PHRASES)
