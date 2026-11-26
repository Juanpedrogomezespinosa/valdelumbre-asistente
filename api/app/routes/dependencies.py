from typing import Annotated

from fastapi import Depends, Request

from app.assistant.answer import AnswerGenerator
from app.assistant.template_generator import TemplateAnswerGenerator
from app.assistant.tourist_office import find_tourist_office
from app.clock import Clock, village_now
from app.data.catalog import Catalog


def get_catalog(request: Request) -> Catalog:
    catalog: Catalog = request.app.state.catalog
    return catalog


def get_clock() -> Clock:
    return village_now


CatalogDep = Annotated[Catalog, Depends(get_catalog)]


def get_answer_generator(catalog: CatalogDep) -> AnswerGenerator:
    return TemplateAnswerGenerator(tourist_office=find_tourist_office(catalog.pois))


ClockDep = Annotated[Clock, Depends(get_clock)]
AnswerGeneratorDep = Annotated[AnswerGenerator, Depends(get_answer_generator)]
