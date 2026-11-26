from collections.abc import Sequence

from app.assistant import template_texts as texts
from app.assistant.answer import Answer
from app.assistant.interpretation.interpretation import Interpretation
from app.assistant.opening_hours_text import opening_hours
from app.assistant.tourist_office import referral
from app.domain.localized_text import Language
from app.domain.poi import Poi


class TemplateAnswerGenerator:
    """Deterministic default generator (D-004).

    It only uses structured fields: descriptions are untrusted text (D-006). What it cannot
    answer is referred to the `tourist_office`, which is named but never cited.
    """

    def __init__(self, tourist_office: Poi | None = None) -> None:
        self._tourist_office = tourist_office

    def generate(
        self, interpretation: Interpretation, pois: Sequence[Poi], language: Language
    ) -> Answer:
        office_referral = referral(self._tourist_office, language)
        if not pois:
            return Answer(text=texts.not_found(language, office_referral), poi_ids=())
        lines = [
            _introduction(interpretation, len(pois), language, office_referral),
            *(_place_line(poi, language, interpretation.asks_hours) for poi in pois),
        ]
        return Answer(text="\n".join(lines), poi_ids=tuple(poi.id for poi in pois))


def _introduction(
    interpretation: Interpretation, count: int, language: Language, office_referral: str | None
) -> str:
    if interpretation.unrecorded:
        cannot = texts.cannot_answer(interpretation.unrecorded, language, office_referral)
        return f"{cannot} {texts.what_i_know(language)}"
    corrects_single_answer = interpretation.asks_for_only_one and count > 1
    return texts.introduction(count, corrects_single_answer, language)


def _place_line(poi: Poi, language: Language, with_hours: bool) -> str:
    seasons = dict.fromkeys(slot.season for slot in poi.schedule.slots if slot.season)
    facts = [
        texts.category(poi.category, language),
        texts.accessibility(poi.accessible, language),
        *(texts.season(season, language) for season in seasons),
        texts.price(poi.price, language),
    ]
    line = f"- {poi.name.resolve(language).text} ({' · '.join(facts)})"
    return f"{line} · {_hours(poi, language)}" if with_hours else line


def _hours(poi: Poi, language: Language) -> str:
    hours = opening_hours(poi.schedule, language, with_seasons=True)
    if language is Language.EN:
        return f"hours: {hours}" if hours else "opening hours unknown"
    return f"horario: {hours}" if hours else "horario sin datos"
