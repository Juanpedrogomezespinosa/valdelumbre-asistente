import re
from collections.abc import Sequence

from app.domain.text_folding import fold

_VILLAGE = "Valdelumbre"
_WORD = re.compile(r"\w+", re.UNICODE)
# A capitalised word that does not start a sentence is taken as a proper name.
_SENTENCE_START = re.compile(r"(^|[.!?¡¿:;]\s*)(\w+)", re.UNICODE)


def names_only_known_places(introduction: str, question: str, place_names: Sequence[str]) -> bool:
    """False if the text names anything (a village, a place) that it was not given (D-048).

    Small models invent names ("Valmundo") even in two sentences; this is the cheapest check
    that catches it. It cannot judge a made-up claim about a known place.
    """
    known = {
        fold(word) for text in (question, _VILLAGE, *place_names) for word in _WORD.findall(text)
    }
    sentence_starts = {match.start(2) for match in _SENTENCE_START.finditer(introduction)}
    return all(
        fold(match.group()) in known
        for match in _WORD.finditer(introduction)
        if match.group()[0].isupper() and match.start() not in sentence_starts
    )
