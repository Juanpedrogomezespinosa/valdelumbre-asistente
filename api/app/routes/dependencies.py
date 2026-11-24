from typing import Annotated

from fastapi import Depends, Request

from app.clock import Clock, village_now
from app.data.catalog import Catalog


def get_catalog(request: Request) -> Catalog:
    catalog: Catalog = request.app.state.catalog
    return catalog


def get_clock() -> Clock:
    return village_now


CatalogDep = Annotated[Catalog, Depends(get_catalog)]
ClockDep = Annotated[Clock, Depends(get_clock)]
