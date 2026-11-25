import logging
import re
from collections.abc import Callable, Sequence

from pydantic import BaseModel, ValidationError

from app.assistant.answer import Answer, AnswerGenerator
from app.assistant.interpretation.interpretation import Interpretation
from app.assistant.introduction_check import names_only_known_places
from app.assistant.llm_prompt import system_prompt, user_message
from app.assistant.template_generator import TemplateAnswerGenerator, place_lines
from app.domain.localized_text import Language
from app.domain.poi import Poi

logger = logging.getLogger("valdelumbre")

Completion = Callable[[str, str], str]
"""(system prompt, user message) -> the model's raw JSON reply. Raises CompletionError."""


class CompletionError(Exception):
    """The model could not be reached or declined to answer."""


class _Reply(BaseModel):
    introduccion: str


_MAX_INTRODUCTION = 400
# A place id ("poi-003") has no business in a sentence for visitors.
_ID_PATTERN = re.compile(r"\bpoi-\d+", re.IGNORECASE)


class LlmAnswerGenerator:
    """Optional generator (D-004, D-048): a language model words the introduction.

    The list of places and the cited ids still come from the code, so the model cannot drop,
    rename or add a place. A false single-place premise is always corrected by the template,
    and any introduction that cannot be trusted falls back to the template as well.
    """

    def __init__(self, complete: Completion, fallback: AnswerGenerator | None = None) -> None:
        self._complete = complete
        self._fallback = fallback or TemplateAnswerGenerator()

    def generate(
        self, interpretation: Interpretation, pois: Sequence[Poi], language: Language
    ) -> Answer:
        corrects_premise = interpretation.asks_for_only_one and len(pois) > 1
        if not pois or corrects_premise:
            return self._fallback.generate(interpretation, pois, language)
        try:
            raw = self._complete(
                system_prompt(language), user_message(interpretation, pois, language)
            )
            introduction = _Reply.model_validate_json(raw).introduccion.strip()
        except (CompletionError, ValidationError) as error:
            logger.warning("LLM answer discarded, using the template: %s", error)
            return self._fallback.generate(interpretation, pois, language)

        names = [poi.name.resolve(language).text for poi in pois]
        if not _trustworthy(introduction) or not names_only_known_places(
            introduction, interpretation.question, names
        ):
            logger.warning("LLM introduction rejected, using the template: %r", introduction)
            return self._fallback.generate(interpretation, pois, language)
        return Answer(
            text="\n".join([introduction, *place_lines(pois, language)]),
            poi_ids=tuple(poi.id for poi in pois),
        )


def _trustworthy(introduction: str) -> bool:
    return (
        0 < len(introduction) <= _MAX_INTRODUCTION
        and "\n" not in introduction
        and not _ID_PATTERN.search(introduction)
    )
