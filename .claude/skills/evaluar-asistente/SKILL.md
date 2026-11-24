---
name: evaluar-asistente
description: Ejecuta los tests y la evaluación de datos/evaluacion.json, interpreta los fallos y propone la causa raíz sin hacer trampas. Usar tras cambiar la recuperación, la interpretación de preguntas o el generador.
---

# Evaluar el asistente

1. `cd api && uv run ruff check . && uv run mypy . && uv run pytest -q`: si algo falla, para y corrígelo antes de evaluar.
2. `cd api && uv run python ../scripts/evaluate.py`: anota los marcadores **oficial** y **estricto**.
3. Para cada pregunta que falle, clasifica la causa:
   - **Interpretación:** la pregunta no se tradujo a los filtros correctos (sinónimo, día u hora, idioma).
   - **Filtro:** los filtros eran correctos pero el dominio falla (horario, accesibilidad, duplicados).
   - **Ranking/umbral:** se recuperó de más o de menos.
   - **Generación:** se recuperó bien pero la respuesta cita mal.
4. Propón un arreglo **general**.

## Prohibido (hacer trampas)
- Hardcodear preguntas, ids o respuestas de `evaluacion.json`.
- Añadir sinónimos que solo sirven para una pregunta concreta sin que tengan sentido general.
- Tocar `evaluacion.json` o relajar el criterio de acierto.

Si una pregunta solo se puede acertar con una de estas trampas, se deja fallando y se explica en `README.md` (qué haría con más tiempo).

5. Registra el resultado (antes → después) en `docs/BITACORA.md`.
