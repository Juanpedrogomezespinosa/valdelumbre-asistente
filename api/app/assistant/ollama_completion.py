import json
import urllib.request
from collections.abc import Callable
from typing import Any

from app.assistant.llm_generator import Completion, CompletionError
from app.assistant.llm_prompt import REPLY_SCHEMA

PostJson = Callable[[str, dict[str, Any]], dict[str, Any]]

# A small model on a CPU (Docker on a Mac has no GPU) is slow; past this, the template answers.
_TIMEOUT_SECONDS = 90.0
# No creativity: the model should reword the facts, not embellish them.
_TEMPERATURE = 0.0


def ollama_completion(base_url: str, model: str, post: PostJson | None = None) -> Completion:
    """A local model served by Ollama behind the Completion contract (D-048). No key, no account."""
    send = post or _post_json
    url = f"{base_url.rstrip('/')}/api/chat"

    def complete(system: str, user: str) -> str:
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # Constrained decoding: the reply always has the shape the generator checks.
            "format": REPLY_SCHEMA,
            "stream": False,
            "options": {"temperature": _TEMPERATURE},
        }
        try:
            response = send(url, body)
        except (OSError, ValueError) as error:
            raise CompletionError(f"{type(error).__name__}: {error}") from error
        content = response.get("message", {}).get("content")
        if not isinstance(content, str):
            raise CompletionError(
                f"Ollama reply without content: {response.get('error', response)}"
            )
        return content

    return complete


def _post_json(url: str, body: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
        reply: dict[str, Any] = json.load(response)
    return reply
