from collections import Counter
from collections.abc import Sequence

from app.assistant.interpretation.interpretation import Interpretation
from app.assistant.interpretation.phrases import words_in
from app.domain.poi import Poi
from app.domain.poi_filter import filter_pois
from app.domain.text_folding import fold

# Words of place names that are also everyday words: alone they name nothing ("what is there
# in the centre?" is not about the Interpretation Centre). Found with a check of every
# distinctive name word in the catalogue (BITACORA, step 16).
_GENERIC_NAME_WORDS = frozenset(
    {
        "main",
        "mayor",
        "centro",
        "centre",
        "tourist",
        "turismo",
        "casa",
        "house",
        "natural",
        "valle",
        "valley",
        "hill",
        "verde",
    }
)


def retrieve(pois: Sequence[Poi], interpretation: Interpretation) -> list[Poi]:
    """Filter with the shared criteria (D-005), then keep what matches the subject.

    The subject is any place the question names or, failing that, its topics. Without a
    subject, the filters alone decide; with nothing recognisable at all, nothing is retrieved.
    """
    candidates = filter_pois(pois, interpretation.criteria)
    # Names are looked up in the whole catalog: a named place that fails the filters
    # must not be silently replaced by other places.
    named = _named_places(pois, interpretation.keywords)
    if named:
        # A named place is the subject: topics its name suggests ("mirador" → views) must
        # not bring in other places.
        mentioned = [poi for poi in candidates if poi.id in named]
        return sorted(mentioned, key=lambda poi: named[poi.id], reverse=True)
    if not interpretation.topics:
        return candidates if interpretation.has_filters else []

    scores = {poi.id: _topic_score(poi, interpretation.topics) for poi in candidates}
    relevant = [poi for poi in candidates if scores[poi.id] > 0]
    return sorted(relevant, key=lambda poi: scores[poi.id], reverse=True)


def named_places(pois: Sequence[Poi], interpretation: Interpretation) -> list[Poi]:
    """The places the question names, wherever they are in the catalog."""
    named = _named_places(pois, interpretation.keywords)
    return [poi for poi in pois if poi.id in named]


def _topic_score(poi: Poi, topics: frozenset[str]) -> int:
    themes = {fold(tag) for tag in poi.tags} | {poi.category.value}
    return len(topics & themes)


def _named_places(pois: Sequence[Poi], keywords: frozenset[str]) -> dict[str, int]:
    """How many question words name each place.

    A word only names a place when no other place's name has it: "park" is in both
    "Alameda Park" and "Cuesta Car Park", so it identifies neither. Generic words also need
    a distinctive companion.
    """
    name_words = {poi.id: _name_words(poi) for poi in pois}
    occurrences = Counter(word for words in name_words.values() for word in words)
    distinctive = {word for word, count in occurrences.items() if count == 1}
    hits: dict[str, int] = {}
    for poi_id, words in name_words.items():
        mentioned = keywords & words & distinctive
        # A common word ("centro", "main") only counts next to a word that is really the name.
        if mentioned - _GENERIC_NAME_WORDS:
            hits[poi_id] = len(mentioned)
    return hits


def _name_words(poi: Poi) -> frozenset[str]:
    return frozenset(words_in(fold(f"{poi.name.es} {poi.name.en or ''}")))
