from functools import cache
from typing import Annotated

from fastapi import Depends, Request

from app.assistant.answer import AnswerGenerator
from app.assistant.llm_generator import LlmAnswerGenerator
from app.assistant.ollama_completion import ollama_completion
from app.assistant.template_generator import TemplateAnswerGenerator
from app.clock import Clock, village_now
from app.data.catalog import Catalog
from app.settings import answer_generator_name, llm_model, ollama_url


def get_catalog(request: Request) -> Catalog:
    catalog: Catalog = request.app.state.catalog
    return catalog


def get_clock() -> Clock:
    return village_now


def get_answer_generator() -> AnswerGenerator:
    if answer_generator_name() == "llm":
        return _llm_generator(ollama_url(), llm_model())
    return TemplateAnswerGenerator()


@cache
def _llm_generator(url: str, model: str) -> AnswerGenerator:
    return LlmAnswerGenerator(ollama_completion(url, model))


CatalogDep = Annotated[Catalog, Depends(get_catalog)]
ClockDep = Annotated[Clock, Depends(get_clock)]
AnswerGeneratorDep = Annotated[AnswerGenerator, Depends(get_answer_generator)]
