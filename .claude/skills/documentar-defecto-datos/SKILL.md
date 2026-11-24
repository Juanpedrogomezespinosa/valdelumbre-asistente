---
name: documentar-defecto-datos
description: Procedimiento para tratar un defecto encontrado en datos/pois.json — test primero, regla genérica en la capa de carga, aviso y entrada en DATOS.md.
---

# Tratar un defecto de datos

Nunca se edita `datos/pois.json`. El defecto se trata así:

1. **Caracterizar:** qué campo, qué POIs, cómo se detecta de forma **genérica** (sin depender del id) y qué riesgo tiene si se ignora.
2. **Test primero** en `api/tests/` (por ejemplo `test_normalization.py`): un caso con el dato real y, si se puede, un caso sintético que pruebe que la regla es genérica.
3. **Regla** en su propio módulo, `api/app/data/rules/<regla>.py`: corrige o marca como desconocido, y emite un aviso estructurado (id del punto, tipo, detalle y acción tomada). Código en inglés y sin comentarios que repitan el código.
4. Ejecuta `cd api && uv run ruff check . && uv run mypy . && uv run pytest` y la evaluación (`uv run python ../scripts/evaluate.py`).
5. **Documenta** en `DATOS.md` con esta plantilla:

   ```markdown
   ### <Nombre del defecto>
   - **Dónde:** <ids / campo>
   - **Qué pasa:** <descripción con el valor real>
   - **Riesgo si se ignora:** <consecuencia para el turista o el sistema>
   - **Qué se ha hecho:** <regla aplicada; enlace a la decisión D-0NN si existe>
   - **Test:** `api/tests/<fichero>::<test>`
   ```

6. Añade una línea a `docs/BITACORA.md`. Tipo de commit para este caso: `fix(datos): <qué se corrige>`.
