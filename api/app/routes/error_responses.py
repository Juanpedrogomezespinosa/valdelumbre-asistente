from typing import Any

from app.domain.localized_text import Language
from app.domain.poi import Category
from app.routes.messages import invalid_parameter, invalid_question, poi_not_found
from app.routes.schemas import ErrorResponse

OpenApiResponses = dict[int | str, dict[str, Any]]


def _error(status: int, description: str, example: str) -> OpenApiResponses:
    # Declaring 422 also replaces FastAPI's default schema, which D-039's handler no longer returns.
    return {
        status: {
            "model": ErrorResponse,
            "description": description,
            "content": {"application/json": {"example": {"detail": example}}},
        }
    }


INVALID_POI_FILTER = _error(
    422,
    "Parámetro no válido, en el idioma pedido",
    invalid_parameter("categoria", [category.value for category in Category], Language.ES),
)
INVALID_LANGUAGE = _error(
    422,
    "Parámetro no válido, en el idioma pedido",
    invalid_parameter("idioma", [language.value for language in Language], Language.ES),
)
INVALID_QUESTION = _error(
    422, "Petición no válida, en el idioma pedido", invalid_question(Language.ES)
)
POI_NOT_FOUND = _error(
    404, "No existe ningún punto con ese id", poi_not_found("poi-999", Language.ES)
)
