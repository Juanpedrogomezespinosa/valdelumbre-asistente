import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.assistant.interpretation.interpretation import interpret
from app.assistant.llm_generator import CompletionError, LlmAnswerGenerator
from app.assistant.template_generator import TemplateAnswerGenerator
from app.domain.localized_text import Language, LocalizedText
from app.domain.poi import Category
from tests.poi_factory import make_poi

NOW = datetime(2026, 11, 25, 10, 0, tzinfo=ZoneInfo("Europe/Madrid"))
MUSEUM = make_poi(
    "poi-003",
    name=LocalizedText(es="Museo del Aceite"),
    category=Category.MUSEUM,
    accessible=True,
)
CENTRE = make_poi(
    "poi-015",
    name=LocalizedText(es="Centro de Interpretación"),
    category=Category.MUSEUM,
    accessible=True,
)
QUESTION = interpret("¿Qué museos son accesibles?", NOW)
TEMPLATE = TemplateAnswerGenerator().generate(QUESTION, [MUSEUM, CENTRE], Language.ES)


class FakeCompletion:
    def __init__(self, reply: str | Exception) -> None:
        self.reply = reply
        self.calls = 0

    def __call__(self, system: str, user: str) -> str:
        self.calls += 1
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def intro(text: str) -> str:
    return json.dumps({"introduccion": text})


def test_the_model_writes_the_introduction_and_the_code_lists_every_place() -> None:
    completion = FakeCompletion(intro("¡Claro! Tienes dos museos accesibles para visitar."))

    answer = LlmAnswerGenerator(completion).generate(QUESTION, [MUSEUM, CENTRE], Language.ES)

    assert answer.text.splitlines() == [
        "¡Claro! Tienes dos museos accesibles para visitar.",
        *TEMPLATE.text.splitlines()[1:],
    ]
    assert answer.poi_ids == ("poi-003", "poi-015")


@pytest.mark.parametrize(
    "bad_reply",
    [
        intro(""),
        intro("Visita:\n- Museo del Aceite"),
        intro("Te recomiendo el poi-003."),
        intro("x" * 401),
        intro("En Valmundo hay dos museos accesibles."),
        "esto no es JSON",
        json.dumps({"respuesta": "otro campo"}),
        CompletionError("timeout"),
    ],
    ids=[
        "empty",
        "own list",
        "leaks an id",
        "too long",
        "invented name",
        "not json",
        "wrong field",
        "failure",
    ],
)
def test_falls_back_to_the_template_when_the_introduction_cannot_be_trusted(
    bad_reply: str | Exception,
) -> None:
    generator = LlmAnswerGenerator(FakeCompletion(bad_reply))

    assert generator.generate(QUESTION, [MUSEUM, CENTRE], Language.ES) == TEMPLATE


def test_does_not_call_the_model_when_nothing_was_retrieved() -> None:
    completion = FakeCompletion(intro("Hay tirolina"))

    answer = LlmAnswerGenerator(completion).generate(QUESTION, [], Language.ES)

    assert completion.calls == 0
    assert answer.poi_ids == ()


def test_a_false_single_place_premise_is_corrected_by_the_template_not_the_model() -> None:
    # Evaluation q5: a small model tends to repeat the premise ("the only place is...").
    question = interpret("¿Cuál es el único sitio accesible del pueblo?", NOW)
    completion = FakeCompletion(intro("El único sitio accesible es el Museo del Aceite."))

    answer = LlmAnswerGenerator(completion).generate(question, [MUSEUM, CENTRE], Language.ES)

    assert completion.calls == 0
    assert answer == TemplateAnswerGenerator().generate(question, [MUSEUM, CENTRE], Language.ES)
