from app.assistant.interpretation.phrases import contains_any

ONLY_ONE_PHRASES = ("unico", "unica", "the only", "only one")


def asks_for_only_one(folded: str) -> bool:
    """Questions like q5 assume a single answer; the reply should correct that premise."""
    return contains_any(folded, ONLY_ONE_PHRASES)
