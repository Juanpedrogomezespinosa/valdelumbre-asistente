from fastapi import APIRouter, HTTPException

from app.domain.localized_text import Language
from app.routes.dependencies import CatalogDep, ClockDep
from app.routes.messages import poi_not_found
from app.routes.presenters.poi import present_poi
from app.routes.schemas import PoiResponse

router = APIRouter(prefix="/pois", tags=["Puntos de interés"])


@router.get("/{poi_id}", summary="Un punto de interés")
def get_poi(
    poi_id: str, catalog: CatalogDep, clock: ClockDep, idioma: Language = Language.ES
) -> PoiResponse:
    poi = catalog.get(poi_id)
    if poi is None:
        raise HTTPException(status_code=404, detail=poi_not_found(poi_id, idioma))
    return present_poi(poi, idioma, clock())
