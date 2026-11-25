from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.localized_text import Language
from app.domain.poi import Category
from app.routes.messages import invalid_parameter, invalid_question, invalid_request_body

_ALLOWED_VALUES: dict[str, list[str]] = {
    "categoria": [category.value for category in Category],
    "accesible": ["true", "false"],
    "idioma": [language.value for language in Language],
}
_MALFORMED_BODY_ERRORS = {"missing", "json_invalid"}


async def localized_validation_error(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    """Replace pydantic's English 422 with a message in the requested language (D-039)."""
    language = _requested_language(request, error.body)
    messages = dict.fromkeys(_message(detail, language) for detail in error.errors())
    return JSONResponse(status_code=422, content={"detail": " ".join(messages)})


def _requested_language(request: Request, body: Any) -> Language:
    requested = request.query_params.get("idioma")
    if requested is None and isinstance(body, dict):
        requested = body.get("idioma")
    try:
        return Language(requested or Language.ES)
    except ValueError:
        return Language.ES


def _message(detail: Any, language: Language) -> str:
    location = detail["loc"]
    if location[0] == "body" and (len(location) == 1 or detail["type"] in _MALFORMED_BODY_ERRORS):
        return invalid_request_body(language)
    name = str(location[-1])
    if name == "pregunta":
        return invalid_question(language)
    return invalid_parameter(name, _ALLOWED_VALUES.get(name, []), language)
