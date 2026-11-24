.DEFAULT_GOAL := help
API_DIR := api

.PHONY: help install test lint format check

help: ## Muestra los comandos disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

install: ## Instala las dependencias exactas del backend (uv.lock)
	cd $(API_DIR) && uv sync --locked

test: ## Ejecuta los tests del backend
	cd $(API_DIR) && uv run pytest

lint: ## Comprueba estilo, formato y tipos del backend
	cd $(API_DIR) && uv run ruff check . && uv run ruff format --check . && uv run mypy .

format: ## Formatea y corrige lo que se pueda de forma automática
	cd $(API_DIR) && uv run ruff format . && uv run ruff check --fix .

check: lint test ## Lint y tests: lo que debe pasar antes de cada commit
