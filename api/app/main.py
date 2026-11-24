import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.data.catalog import Catalog, load_catalog
from app.settings import catalog_path

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s - %(message)s")
logger = logging.getLogger("valdelumbre")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    catalog = load_catalog(catalog_path())
    _log_data_warnings(catalog)
    app.state.catalog = catalog
    yield


def _log_data_warnings(catalog: Catalog) -> None:
    logger.info(
        "Catalog loaded: %d POIs, %d data warnings", len(catalog.pois), len(catalog.warnings)
    )
    for warning in catalog.warnings:
        logger.warning(
            "%s %s: %s -> %s", warning.poi_id, warning.kind, warning.detail, warning.action
        )


app = FastAPI(title="Valdelumbre · Asistente turístico", lifespan=lifespan)
