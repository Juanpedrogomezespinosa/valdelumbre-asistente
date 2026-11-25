from fastapi import APIRouter

from app.assistant.answer_question import answer_question
from app.routes.dependencies import AnswerGeneratorDep, CatalogDep, ClockDep
from app.routes.error_responses import INVALID_QUESTION
from app.routes.schemas import AskRequest, AskResponse

router = APIRouter(tags=["Asistente"], responses=INVALID_QUESTION)


@router.post("/preguntar", summary="Preguntar al asistente")
def ask(
    request: AskRequest, catalog: CatalogDep, clock: ClockDep, generator: AnswerGeneratorDep
) -> AskResponse:
    answer = answer_question(request.pregunta, request.idioma, catalog.pois, clock(), generator)
    return AskResponse(respuesta=answer.text, ids=list(answer.poi_ids))
