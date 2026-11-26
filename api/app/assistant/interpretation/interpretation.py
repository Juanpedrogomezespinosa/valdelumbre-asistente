from dataclasses import dataclass
from datetime import datetime

from app.assistant.interpretation.accessibility import (
    ACCESSIBILITY_PHRASES,
    UNKNOWN_ACCESSIBILITY_PHRASES,
    accessibility_in,
)
from app.assistant.interpretation.categories import CATEGORY_PHRASES, categories_in
from app.assistant.interpretation.closed import CLOSED_PHRASES, asks_closed
from app.assistant.interpretation.hours import HOURS_PHRASES, asks_hours
from app.assistant.interpretation.name_synonyms import NAME_SYNONYM_PHRASES, name_words_in
from app.assistant.interpretation.only_one import ONLY_ONE_PHRASES, asks_for_only_one
from app.assistant.interpretation.opening_time import TIME_WORDS, now_query, opening_query_in
from app.assistant.interpretation.phrases import contains_any, words_in, words_of
from app.assistant.interpretation.price import (
    CHEAPEST_PHRASES,
    FREE_PHRASES,
    price_under,
    wants_cheapest,
    wants_free,
)
from app.assistant.interpretation.sights import SIGHTS_PHRASES, asks_for_sights
from app.assistant.interpretation.topics import TOPIC_PHRASES, topics_in
from app.assistant.interpretation.unrecorded import UNRECORDED_PHRASES, unrecorded_in
from app.domain.poi_filter import PoiCriteria
from app.domain.text_folding import fold

_MIN_KEYWORD_LENGTH = 4
# Asking the price is answered by the price on every line, so these words never name places.
_PRICE_QUESTION = ("cuanto", "precio", "precios")
_PRICE_WORDS = (
    "cuanto",
    "precio",
    "precios",
    "price",
    "prices",
    "cost",
    "costs",
    "menos",
    "euro",
    "euros",
    "under",
    "dinero",
    "money",
)
_VILLAGE_WORDS = frozenset({"valdelumbre", "pueblo", "village", "town"})
_INTERPRETED_WORDS = words_of(
    (
        *ACCESSIBILITY_PHRASES,
        *CATEGORY_PHRASES,
        *TOPIC_PHRASES,
        *TIME_WORDS,
        *ONLY_ONE_PHRASES,
        *UNRECORDED_PHRASES,
        *_PRICE_WORDS,
        *UNKNOWN_ACCESSIBILITY_PHRASES,
        *CLOSED_PHRASES,
        *HOURS_PHRASES,
        *FREE_PHRASES,
        *CHEAPEST_PHRASES,
        *SIGHTS_PHRASES,
        *NAME_SYNONYM_PHRASES,
    )
    # "Cuesta" is also the car park's name; _keywords decides when it is a price word.
) - {"cuesta", "cuestan"}


@dataclass(frozen=True)
class Interpretation:
    criteria: PoiCriteria
    topics: frozenset[str]
    keywords: frozenset[str]
    """Words left once the vocabulary is interpreted, to match place names."""
    asks_for_only_one: bool
    unrecorded: frozenset[str] = frozenset()
    """What the question asks about that the assistant does not look up (D-050)."""
    asks_hours: bool = False
    """Each place in the answer then says its opening hours."""
    asks_for_sights: bool = False
    """«Qué ver»: without another subject, only places worth visiting."""
    asks_for_cheapest: bool = False

    @property
    def has_filters(self) -> bool:
        criteria = self.criteria
        return (
            criteria.categories is not None
            or criteria.accessible is not None
            or criteria.accessibility_unknown
            or criteria.open_at is not None
            or criteria.free
            or criteria.price_under is not None
            or self.asks_for_sights
            or self.asks_for_cheapest
        )


def interpret(question: str, now: datetime) -> Interpretation:
    folded = fold(question)
    accessible, accessibility_unknown = accessibility_in(folded)
    closed = asks_closed(folded)
    open_at = opening_query_in(folded, now)
    under = price_under(folded)
    return Interpretation(
        criteria=PoiCriteria(
            categories=categories_in(folded) or None,
            accessible=accessible,
            accessibility_unknown=accessibility_unknown,
            # "¿Qué está cerrado?" without a moment asks about now.
            open_at=open_at or (now_query(now) if closed else None),
            closed=closed,
            free=wants_free(folded),
            price_under=under,
        ),
        topics=topics_in(folded),
        keywords=_keywords(folded, asks_price=under is not None) | name_words_in(folded),
        asks_for_only_one=asks_for_only_one(folded),
        unrecorded=unrecorded_in(folded),
        asks_hours=asks_hours(folded),
        asks_for_sights=asks_for_sights(folded),
        asks_for_cheapest=wants_cheapest(folded),
    )


def _keywords(folded: str, *, asks_price: bool) -> frozenset[str]:
    words = frozenset(
        word
        for word in words_in(folded)
        if len(word) >= _MIN_KEYWORD_LENGTH
        and word not in _INTERPRETED_WORDS
        and word not in _VILLAGE_WORDS
    )
    # "¿Cuánto cuesta…?" asks a price; otherwise "Cuesta" may be the car park's name, which is
    # its only distinctive word in English ("Cuesta Car Park").
    if asks_price or contains_any(folded, _PRICE_QUESTION):
        return words - {"cuesta", "cuestan"}
    return words
