from app.assistant.interpretation.phrases import contains_any

NEARBY_PHRASES = (
    "cerca de",
    "cerca del",
    "cercano a",
    "cercanos a",
    "cercana a",
    "cercanas a",
    "al lado de",
    "al lado del",
    "junto a",
    "junto al",
    "near",
    "nearby",
    "close to",
    "next to",
)


def asks_nearby(folded: str) -> bool:
    return contains_any(folded, NEARBY_PHRASES)
