from app.assistant.interpretation.phrases import contains_any
from app.domain.poi import Category

SIGHTS_PHRASES = (
    "que ver",
    "que visitar",
    "puedo visitar",
    "que hacer",
    "puedo hacer",
    "que hago",
    "que hacemos",
    "podemos hacer",
    "podemos ver",
    "lugares de interes",
    "sitios de interes",
    "que me recomiendas",
    "recomiendame",
    "things to do",
    "what to see",
    "what to visit",
    "what can i do",
    "what can i see",
    "what can i visit",
    "places to visit",
    "sightseeing",
)
# What a visitor goes to see or do; services and places to eat are not sights.
SIGHT_CATEGORIES = frozenset(
    {Category.MONUMENT, Category.MUSEUM, Category.NATURE, Category.ROUTE, Category.PUBLIC_SPACE}
)


def asks_for_sights(folded: str) -> bool:
    return contains_any(folded, SIGHTS_PHRASES)
