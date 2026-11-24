# Asistente turístico de Valdelumbre · Reglas del proyecto

Prueba técnica: API (FastAPI) + asistente que responde **solo** con el catálogo + pantalla Angular accesible.
Enunciado: `../ENUNCIADO.md` (fuera del repo). Decisiones ya tomadas: `docs/DECISIONES.md`. **No volver a discutirlas** sin proponer antes una revisión explícita.

## Forma de trabajar (obligatorio)
1. **Preguntar antes de decidir.** Antes de crear o cambiar convenciones, reglas, skills o configuración, pregunta al autor y espera su respuesta.
2. **Primero proponer, luego programar.** Ante cualquier cambio no trivial: explica el plan y espera aprobación.
3. **Documentar cada paso.** Al terminar uno:
   - entrada en `docs/BITACORA.md` (qué se hizo, por qué y con qué herramienta);
   - decisión nueva → `docs/DECISIONES.md` (skill `registrar-decision`);
   - defecto de datos → `DATOS.md` (skill `documentar-defecto-datos`);
   - lo que la IA propuso y se corrigió o descartó → anotarlo para `IA.md`.
4. **No inventar**, ni en el asistente ni en la documentación.

## Código limpio (D-021 a D-024)
- **Idioma:** código en **inglés** (clases, funciones, variables, ficheros y carpetas). Los nombres de los campos del JSON y de la API se mantienen tal como los define el enunciado (`categoria`, `accesible`, `abierto_en`, `/preguntar`). Documentación en español.
- **Comentarios mínimos:** el código se explica con nombres expresivos y funciones pequeñas. Un comentario solo justifica un **porqué** que no sea evidente (una regla de negocio, un dato deducido o un workaround). Nunca parafrasea el código. Docstring solo en la interfaz pública no trivial. Comentarios en inglés.
  - ❌ `# check if the poi is accessible` encima de `if poi.accessible:`
  - ✅ `# ISO weekdays (1 = Monday): inferred from evaluacion.json q3`
- **Antes de entregar cualquier cambio**, revisa y elimina: comentarios que repiten el código, código muerto, abstracciones especulativas ("por si acaso"), nombres genéricos (`data`, `info`, `helper`, `utils`) y funciones que hacen más de una cosa.
- **Calidad automática:** backend con `ruff` (lint + formato) y `mypy --strict`; frontend con `angular-eslint` + Prettier. Deben pasar en limpio.
- **TDD en el núcleo:** test primero en la normalización de datos, los horarios, la interpretación de preguntas y los filtros. Sin objetivo numérico de cobertura.
- **Errores de la API** en el idioma pedido (es/en): los ve el usuario final.

## Git (D-025)
- Una rama por bloque (`feat/api-data`, `feat/assistant`, `feat/web`…), que se fusiona en `main` cuando sus tests y linters pasan.
- Conventional Commits: prefijo estándar y descripción en español. Ej.: `feat(api): filtro abierto_en con días ISO`.
- **Git lo gestiona el autor**: commits, ramas, merges y push. La IA no ejecuta comandos de Git que escriban; solo puede leer (`git status`, `git diff`, `git log`) y, al terminar un bloque, sugerir el mensaje de commit.

## Invariantes del producto (no romper)
- `datos/*.json` **no se modifica nunca**. Toda corrección va en `api/app/data/` como regla + test.
- Accesibilidad, horario y categoría se deciden con **campos estructurados**, jamás leyendo la descripción.
- `accesible` es tri-estado (`true`/`false`/`null`); un horario sin franjas y sin `always_open` es **desconocido**, no cerrado.
- Días 1–7 = lunes–domingo (ISO). Zona horaria `Europe/Madrid`.
- `/preguntar` solo cita ids que existan en el catálogo servido y que hayan sido recuperados.
- Los tests y la evaluación se ejecutan **sin red**.

## Comandos
- API: `cd api && uv run uvicorn app.main:app --reload`
- Calidad API: `cd api && uv run ruff check . && uv run ruff format --check . && uv run mypy .`
- Tests API: `cd api && uv run pytest`
- Evaluación: `cd api && uv run python ../scripts/evaluate.py`
- Web: `cd web && npm start` · tests: `npm test` · lint: `npm run lint`
- Todo: `docker compose up --build`

Reglas por área en `.claude/rules/`.
