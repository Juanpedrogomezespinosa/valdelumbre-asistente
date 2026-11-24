---
paths:
  - "api/**"
  - "scripts/**"
---

# Reglas · Backend (FastAPI)

- Python 3.12, dependencias con `uv` (`uv add`, nunca `pip install`). Tipado completo; modelos con Pydantic v2.
- Capas y dependencias en un solo sentido: `routes → assistant → domain ← data`. `domain` no importa FastAPI.
- La hora actual **se inyecta** (un reloj) en todo lo que dependa de ella; nada de `datetime.now()` disperso.
- El generador de respuestas se usa siempre a través de la interfaz `AnswerGenerator`. Ningún test puede requerir red ni clave.
- Los filtros de `GET /pois` y los de `/preguntar` usan **la misma función**: una única fuente de verdad.
- Errores de entrada → 422 con un mensaje útil en el idioma pedido (es/en); id inexistente → 404. Nunca 500 por datos de usuario.
- Cada regla de normalización o de interpretación de preguntas nueva lleva su test (pytest, `TestClient` para endpoints).
- Tests primero en el núcleo (normalización, horarios, interpretación de preguntas y filtros).
- Antes de dar algo por terminado: `uv run ruff check .`, `uv run ruff format --check .` y `uv run mypy .` limpios, `uv run pytest` en verde y `uv run python ../scripts/evaluate.py` sin regresiones.
