from datetime import time

from pydantic import BaseModel, ConfigDict

from app.data.rules.price import RawPrice
from app.domain.poi import Category


class _RawModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class RawText(_RawModel):
    es: str
    en: str | None = None


class RawSlot(_RawModel):
    dias: list[int]
    abre: time
    cierra: time
    temporada: str | None = None


class RawSchedule(_RawModel):
    always_open: bool
    franjas: list[RawSlot]


class RawPoi(_RawModel):
    id: str
    nombre: RawText
    categoria: Category
    descripcion: RawText
    lat: float
    lon: float
    accesible: bool | None
    horario: RawSchedule
    precio: RawPrice
    etiquetas: list[str]
