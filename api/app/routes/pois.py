from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.domain.localized_text import Language
from app.domain.opening_query import OpeningQuery
from app.domain.poi import Category
from app.domain.poi_filter import PoiCriteria, filter_pois
from app.routes.dependencies import CatalogDep, ClockDep
from app.routes.messages import invalid_open_at, poi_not_found
from app.routes.open_at_param import parse_open_at
from app.routes.presenters.poi import present_poi
from app.routes.schemas import PoiResponse

router = APIRouter(prefix="/pois", tags=["Puntos de interés"])


@router.get("", summary="Puntos de interés con filtros")
def list_pois(
    catalog: CatalogDep,
    clock: ClockDep,
    categoria: Category | None = None,
    accesible: bool | None = None,
    abierto_en: str | None = None,
    idioma: Language = Language.ES,
) -> list[PoiResponse]:
    now = clock()
    criteria = PoiCriteria(
        category=categoria,
        accessible=accesible,
        open_at=None if abierto_en is None else _opening_query(abierto_en, now, idioma),
    )
    return [present_poi(poi, idioma, now) for poi in filter_pois(catalog.pois, criteria)]


@router.get("/{poi_id}", summary="Un punto de interés")
def get_poi(
    poi_id: str, catalog: CatalogDep, clock: ClockDep, idioma: Language = Language.ES
) -> PoiResponse:
    poi = catalog.get(poi_id)
    if poi is None:
        raise HTTPException(status_code=404, detail=poi_not_found(poi_id, idioma))
    return present_poi(poi, idioma, clock())


def _opening_query(abierto_en: str, now: datetime, language: Language) -> OpeningQuery:
    try:
        return parse_open_at(abierto_en, now)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=invalid_open_at(language)) from error
