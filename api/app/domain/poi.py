from dataclasses import dataclass
from enum import StrEnum

from app.domain.coordinates import Coordinates
from app.domain.localized_text import LocalizedText
from app.domain.price import Price
from app.domain.schedule import Schedule


class Category(StrEnum):
    MONUMENT = "monumento"
    MUSEUM = "museo"
    NATURE = "naturaleza"
    ROUTE = "ruta"
    GASTRONOMY = "gastronomia"
    SERVICE = "servicio"
    PUBLIC_SPACE = "espacio_publico"


@dataclass(frozen=True)
class Poi:
    id: str
    name: LocalizedText
    category: Category
    description: LocalizedText
    coordinates: Coordinates | None
    accessible: bool | None
    schedule: Schedule
    price: Price
    tags: tuple[str, ...]
