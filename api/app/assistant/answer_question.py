from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime

from app.assistant.answer import Answer, AnswerGenerator
from app.assistant.interpretation.interpretation import interpret
from app.assistant.retrieval import retrieve
from app.domain.localized_text import Language
from app.domain.poi import Poi


def answer_question(
    question: str,
    language: Language,
    pois: Sequence[Poi],
    now: datetime,
    generator: AnswerGenerator,
) -> Answer:
    """Interpret, retrieve with the shared filters and generate, in that order (D-005)."""
    interpretation = interpret(question, now)
    retrieved = retrieve(pois, interpretation)
    answer = generator.generate(interpretation, retrieved, language)
    return _citing_only(retrieved, answer)


def _citing_only(retrieved: Sequence[Poi], answer: Answer) -> Answer:
    # Whatever the generator writes (an LLM could invent ids), only retrieved places are cited.
    allowed = {poi.id for poi in retrieved}
    return replace(answer, poi_ids=tuple(poi_id for poi_id in answer.poi_ids if poi_id in allowed))
