from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from app.assistant.interpretation.interpretation import Interpretation
from app.domain.localized_text import Language
from app.domain.poi import Poi


@dataclass(frozen=True)
class Answer:
    text: str
    poi_ids: tuple[str, ...]


class AnswerGenerator(Protocol):
    """Writes the reply from places already retrieved; swappable for an LLM (D-004)."""

    def generate(
        self, interpretation: Interpretation, pois: Sequence[Poi], language: Language
    ) -> Answer: ...
