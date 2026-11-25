from collections.abc import Sequence

from app.assistant import template_texts as texts
from app.assistant.answer import Answer
from app.assistant.interpretation.interpretation import Interpretation
from app.domain.localized_text import Language
from app.domain.poi import Poi


class TemplateAnswerGenerator:
    """Deterministic default generator (D-004).

    It only uses structured fields: descriptions are untrusted text (D-006).
    """

    def generate(
        self, interpretation: Interpretation, pois: Sequence[Poi], language: Language
    ) -> Answer:
        if not pois:
            return Answer(text=texts.not_found(language), poi_ids=())
        corrects_single_answer = interpretation.asks_for_only_one and len(pois) > 1
        lines = [
            texts.introduction(len(pois), corrects_single_answer, language),
            *place_lines(pois, language),
        ]
        return Answer(text="\n".join(lines), poi_ids=tuple(poi.id for poi in pois))


def place_lines(pois: Sequence[Poi], language: Language) -> list[str]:
    """One "- name (facts)" line per place, from structured fields only."""
    return [_place_line(poi, language) for poi in pois]


def _place_line(poi: Poi, language: Language) -> str:
    seasons = dict.fromkeys(slot.season for slot in poi.schedule.slots if slot.season)
    facts = [
        texts.category(poi.category, language),
        texts.accessibility(poi.accessible, language),
        *(texts.season(season, language) for season in seasons),
    ]
    return f"- {poi.name.resolve(language).text} ({' · '.join(facts)})"
