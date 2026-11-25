.DEFAULT_GOAL := help
API_DIR := api
WEB_DIR := web
API_PORT ?= 8000

.PHONY: help install api web up down test eval lint format check

help: ## Muestra los comandos disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

install: ## Instala las dependencias exactas del backend (uv.lock) y del frontend (package-lock)
	cd $(API_DIR) && uv sync --locked
	cd $(WEB_DIR) && npm ci

api: ## Levanta la API con recarga automática en http://localhost:$(API_PORT)
	cd $(API_DIR) && uv run uvicorn app.main:app --reload --port $(API_PORT)

web: ## Levanta la web en http://localhost:4200 (necesita la API en marcha: make api)
	cd $(WEB_DIR) && npm start

up: ## Construye y levanta todo con Docker: web en http://localhost:8080, API en :8000
	docker compose up --build

down: ## Para y elimina los contenedores de Docker
	docker compose down

test: ## Ejecuta los tests del backend y del frontend
	cd $(API_DIR) && uv run pytest
	cd $(WEB_DIR) && npm test

eval: ## Evalúa el asistente con datos/evaluacion.json (EVAL_URL=http://… para un servidor)
	cd $(API_DIR) && uv run python ../scripts/evaluate.py $(if $(EVAL_URL),--url $(EVAL_URL))

lint: ## Comprueba estilo, formato y tipos del backend, los scripts y el frontend
	cd $(API_DIR) && uv run ruff check . ../scripts && uv run ruff format --check . ../scripts \
		&& uv run mypy . ../scripts
	cd $(WEB_DIR) && npm run lint && npm run format:check

format: ## Formatea y corrige lo que se pueda de forma automática
	cd $(API_DIR) && uv run ruff format . ../scripts && uv run ruff check --fix . ../scripts
	cd $(WEB_DIR) && npm run format

check: lint test ## Lint y tests: lo que debe pasar antes de cada commit
