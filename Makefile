.DEFAULT_GOAL := help
API_DIR := api
API_PORT ?= 8000

.PHONY: help install api test eval lint format check

help: ## Muestra los comandos disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

install: ## Instala las dependencias exactas del backend (uv.lock)
	cd $(API_DIR) && uv sync --locked

api: ## Levanta la API con recarga automática en http://localhost:$(API_PORT)
	cd $(API_DIR) && uv run uvicorn app.main:app --reload --port $(API_PORT)

test: ## Ejecuta los tests del backend
	cd $(API_DIR) && uv run pytest

eval: ## Evalúa el asistente con datos/evaluacion.json (EVAL_URL=http://… para un servidor)
	cd $(API_DIR) && uv run python ../scripts/evaluate.py $(if $(EVAL_URL),--url $(EVAL_URL))

lint: ## Comprueba estilo, formato y tipos del backend y de los scripts
	cd $(API_DIR) && uv run ruff check . ../scripts && uv run ruff format --check . ../scripts \
		&& uv run mypy . ../scripts

format: ## Formatea y corrige lo que se pueda de forma automática
	cd $(API_DIR) && uv run ruff format . ../scripts && uv run ruff check --fix . ../scripts

check: lint test ## Lint y tests: lo que debe pasar antes de cada commit
