from collections import Counter
from collections.abc import Sequence

from app.assistant.interpretation.interpretation import Interpretation
from app.assistant.interpretation.phrases import words_in
from app.domain.poi import Poi
from app.domain.poi_filter import filter_pois
from app.domain.text_folding import fold


def retrieve(pois: Sequence[Poi], interpretation: Interpretation) -> list[Poi]:
    """Filter with the shared criteria (D-005), then keep what matches the subject.

    The subject is the question's topics and any place it names. Without a subject,
    the filters alone decide; with nothing recognisable at all, nothing is retrieved.
    """
    candidates = filter_pois(pois, interpretation.criteria)
    # Names are looked up in the whole catalog: a named place that fails the filters
    # must not be silently replaced by other places.
    named = _named_places(pois, interpretation.keywords)
    if not interpretation.topics and not named:
        return candidates if interpretation.has_filters else []

    scores = {
        poi.id: _topic_score(poi, interpretation.topics) + named.get(poi.id, 0)
        for poi in candidates
    }
    relevant = [poi for poi in candidates if scores[poi.id] > 0]
    return sorted(relevant, key=lambda poi: scores[poi.id], reverse=True)


def _topic_score(poi: Poi, topics: frozenset[str]) -> int:
    themes = {fold(tag) for tag in poi.tags} | {poi.category.value}
    return len(topics & themes)


def _named_places(pois: Sequence[Poi], keywords: frozenset[str]) -> dict[str, int]:
    """How many question words name each place.

    A word only names a place when no other place's name has it: "park" is in both
    "Alameda Park" and "Cuesta Car Park", so it identifies neither.
    """
    name_words = {poi.id: _name_words(poi) for poi in pois}
    occurrences = Counter(word for words in name_words.values() for word in words)
    distinctive = {word for word, count in occurrences.items() if count == 1}
    hits = {poi_id: len(keywords & words & distinctive) for poi_id, words in name_words.items()}
    return {poi_id: count for poi_id, count in hits.items() if count}


def _name_words(poi: Poi) -> frozenset[str]:
    return frozenset(words_in(fold(f"{poi.name.es} {poi.name.en or ''}")))
