from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.localized_text import Language
from app.domain.poi import Category
from app.routes.messages import invalid_parameter

_ALLOWED_VALUES: dict[str, list[str]] = {
    "categoria": [category.value for category in Category],
    "accesible": ["true", "false"],
    "idioma": [language.value for language in Language],
}


async def localized_validation_error(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    """Replace pydantic's English 422 with a message in the requested language (D-039)."""
    language = _requested_language(request)
    messages = dict.fromkeys(
        invalid_parameter(name, _ALLOWED_VALUES.get(name, []), language)
        for name in _invalid_parameter_names(error)
    )
    return JSONResponse(status_code=422, content={"detail": " ".join(messages)})


def _requested_language(request: Request) -> Language:
    try:
        return Language(request.query_params.get("idioma", Language.ES))
    except ValueError:
        return Language.ES


def _invalid_parameter_names(error: RequestValidationError) -> list[str]:
    return [str(detail["loc"][-1]) for detail in error.errors()]
