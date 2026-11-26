from app.assistant.interpretation.phrases import contains_any

# Ways of asking for a place that are not words of its name.
_SYNONYMS = {
    "aparcamiento": (
        "aparcar",
        "aparco",
        "aparcamos",
        "aparcamientos",
        "parking",
        "parkings",
        "car park",
        "park the car",
    ),
}

NAME_SYNONYM_PHRASES = tuple(phrase for phrases in _SYNONYMS.values() for phrase in phrases)


def name_words_in(folded: str) -> frozenset[str]:
    return frozenset(name for name, phrases in _SYNONYMS.items() if contains_any(folded, phrases))
