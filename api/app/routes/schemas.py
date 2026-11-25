from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.domain.localized_text import Language
from app.domain.poi import Category


class ErrorResponse(BaseModel):
    detail: str


MAX_QUESTION_LENGTH = 500


class AskRequest(BaseModel):
    pregunta: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_QUESTION_LENGTH)
    ]
    idioma: Language = Language.ES


class AskResponse(BaseModel):
    respuesta: str
    ids: list[str]


class TextResponse(BaseModel):
    texto: str
    idioma: Language


class CoordinatesResponse(BaseModel):
    lat: float
    lon: float


class SeasonResponse(BaseModel):
    desde: str
    hasta: str


class SlotResponse(BaseModel):
    dias: list[int]
    abre: str
    cierra: str
    temporada: SeasonResponse | None


class ScheduleResponse(BaseModel):
    siempre_abierto: bool
    conocido: bool
    franjas: list[SlotResponse]


class PriceResponse(BaseModel):
    minimo: float | None
    maximo: float | None
    texto: str


class PoiResponse(BaseModel):
    id: str
    nombre: TextResponse
    descripcion: TextResponse
    categoria: Category
    coordenadas: CoordinatesResponse | None
    accesible: bool | None
    abierto_ahora: bool | None
    horario: ScheduleResponse
    precio: PriceResponse
    etiquetas: list[str]
