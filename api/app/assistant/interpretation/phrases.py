import re
from collections.abc import Iterable
from functools import cache

_WORD = re.compile(r"[a-z0-9]+")


def contains_any(folded: str, phrases: Iterable[str]) -> bool:
    return any(_whole_phrase(phrase).search(folded) for phrase in phrases)


def words_in(folded: str) -> list[str]:
    return _WORD.findall(folded)


def words_of(phrases: Iterable[str]) -> frozenset[str]:
    return frozenset(word for phrase in phrases for word in words_in(phrase))


@cache
def _whole_phrase(phrase: str) -> re.Pattern[str]:
    return re.compile(rf"\b{re.escape(phrase)}\b")
