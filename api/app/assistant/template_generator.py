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
        lines = [
            _introduction(interpretation, len(pois), language),
            *(_place_line(poi, language) for poi in pois),
        ]
        return Answer(text="\n".join(lines), poi_ids=tuple(poi.id for poi in pois))


def _introduction(interpretation: Interpretation, count: int, language: Language) -> str:
    if interpretation.unrecorded:
        cannot = texts.cannot_answer(interpretation.unrecorded, language)
        return f"{cannot} {texts.what_i_know(language)}"
    corrects_single_answer = interpretation.asks_for_only_one and count > 1
    return texts.introduction(count, corrects_single_answer, language)


def _place_line(poi: Poi, language: Language) -> str:
    seasons = dict.fromkeys(slot.season for slot in poi.schedule.slots if slot.season)
    facts = [
        texts.category(poi.category, language),
        texts.accessibility(poi.accessible, language),
        *(texts.season(season, language) for season in seasons),
        texts.price(poi.price, language),
    ]
    return f"- {poi.name.resolve(language).text} ({' · '.join(facts)})"
