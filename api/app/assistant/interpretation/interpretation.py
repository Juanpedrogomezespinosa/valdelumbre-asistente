from dataclasses import dataclass
from datetime import datetime

from app.assistant.interpretation.accessibility import ACCESSIBILITY_PHRASES, wants_accessible
from app.assistant.interpretation.categories import CATEGORY_PHRASES, categories_in
from app.assistant.interpretation.only_one import ONLY_ONE_PHRASES, asks_for_only_one
from app.assistant.interpretation.opening_time import TIME_WORDS, opening_query_in
from app.assistant.interpretation.phrases import words_in, words_of
from app.assistant.interpretation.topics import TOPIC_PHRASES, topics_in
from app.domain.poi_filter import PoiCriteria
from app.domain.text_folding import fold

_MIN_KEYWORD_LENGTH = 4
_VILLAGE_WORDS = frozenset({"valdelumbre", "pueblo", "village", "town"})
_INTERPRETED_WORDS = words_of(
    (*ACCESSIBILITY_PHRASES, *CATEGORY_PHRASES, *TOPIC_PHRASES, *TIME_WORDS, *ONLY_ONE_PHRASES)
)


@dataclass(frozen=True)
class Interpretation:
    criteria: PoiCriteria
    topics: frozenset[str]
    keywords: frozenset[str]
    """Words left once the vocabulary is interpreted, to match place names."""
    asks_for_only_one: bool
    question: str = ""
    """The question as asked, for generators that write free text (D-048)."""

    @property
    def has_filters(self) -> bool:
        criteria = self.criteria
        return (
            criteria.categories is not None
            or criteria.accessible is not None
            or criteria.open_at is not None
        )


def interpret(question: str, now: datetime) -> Interpretation:
    folded = fold(question)
    return Interpretation(
        criteria=PoiCriteria(
            categories=categories_in(folded) or None,
            accessible=True if wants_accessible(folded) else None,
            open_at=opening_query_in(folded, now),
        ),
        topics=topics_in(folded),
        keywords=_keywords(folded),
        asks_for_only_one=asks_for_only_one(folded),
        question=question,
    )


def _keywords(folded: str) -> frozenset[str]:
    return frozenset(
        word
        for word in words_in(folded)
        if len(word) >= _MIN_KEYWORD_LENGTH
        and word not in _INTERPRETED_WORDS
        and word not in _VILLAGE_WORDS
    )
