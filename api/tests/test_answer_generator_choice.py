import pytest

from app.assistant.llm_generator import LlmAnswerGenerator
from app.assistant.template_generator import TemplateAnswerGenerator
from app.routes.dependencies import get_answer_generator


def test_the_template_is_the_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GENERADOR", raising=False)

    assert isinstance(get_answer_generator(), TemplateAnswerGenerator)


def test_the_language_model_is_used_only_when_asked_for(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GENERADOR", "llm")

    assert isinstance(get_answer_generator(), LlmAnswerGenerator)
