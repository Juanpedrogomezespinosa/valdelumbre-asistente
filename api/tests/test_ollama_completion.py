import json
from typing import Any

import pytest

from app.assistant.llm_generator import CompletionError
from app.assistant.llm_prompt import REPLY_SCHEMA
from app.assistant.ollama_completion import ollama_completion


class FakePost:
    def __init__(self, response: dict[str, Any] | Exception) -> None:
        self.response = response
        self.sent: list[tuple[str, dict[str, Any]]] = []

    def __call__(self, url: str, body: dict[str, Any]) -> dict[str, Any]:
        self.sent.append((url, body))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def test_asks_ollama_for_a_reply_that_follows_the_schema() -> None:
    post = FakePost(
        {"message": {"role": "assistant", "content": '{"respuesta": "Hola", "ids": []}'}}
    )
    complete = ollama_completion("http://ollama:11434", "qwen2.5:3b", post)

    assert complete("sistema", "usuario") == '{"respuesta": "Hola", "ids": []}'

    url, body = post.sent[0]
    assert url == "http://ollama:11434/api/chat"
    assert body["model"] == "qwen2.5:3b"
    assert body["format"] == REPLY_SCHEMA
    assert body["stream"] is False
    assert body["messages"] == [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "usuario"},
    ]
    json.dumps(body)


@pytest.mark.parametrize(
    "response",
    [OSError("connection refused"), TimeoutError(), {"error": "model not found"}, {"message": {}}],
    ids=["unreachable", "timeout", "ollama error", "no content"],
)
def test_any_failure_becomes_a_completion_error(response: dict[str, Any] | Exception) -> None:
    complete = ollama_completion("http://ollama:11434", "qwen2.5:3b", FakePost(response))

    with pytest.raises(CompletionError):
        complete("sistema", "usuario")
