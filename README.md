# Valdelumbre · Asistente turístico

Asistente turístico para el pueblo (ficticio) de Valdelumbre:
- una **API** (FastAPI) con el catálogo de puntos de interés y un endpoint de preguntas;
- un **asistente** que responde **solo** con lo que hay en el catálogo y cita los puntos en los que se apoya;
- una **pantalla** (Angular) usable con teclado y con lector de pantalla.

> 🚧 **Estado:** en construcción. Este README se actualiza en cada paso; los comandos marcados con ⏳ aún no están implementados.

---

## Índice
1. [Arranque rápido (un comando)](#1-arranque-rápido-un-comando)
2. [Requisitos](#2-requisitos)
3. [Arranque paso a paso con Docker](#3-arranque-paso-a-paso-con-docker)
4. [Arranque sin Docker (desarrollo)](#4-arranque-sin-docker-desarrollo)
5. [Tests y evaluación](#5-tests-y-evaluación)
6. [Uso de la API](#6-uso-de-la-api)
7. [Configuración](#7-configuración)
8. [Estructura del repositorio](#8-estructura-del-repositorio)
9. [Decisiones principales](#9-decisiones-principales)
10. [Qué haría con más tiempo](#10-qué-haría-con-más-tiempo)
11. [Problemas frecuentes](#11-problemas-frecuentes)
12. [Documentación relacionada](#12-documentación-relacionada)

---

## 1. Arranque rápido (un comando)

⏳ Con Docker instalado y en marcha:

```bash
git clone <url-del-repositorio> valdelumbre-asistente
cd valdelumbre-asistente
docker compose up --build
```

Cuando termine de construir:

| Qué | URL |
|-----|-----|
| Pantalla (web) | http://localhost:8080 |
| API | http://localhost:8000 |
| Documentación interactiva de la API (Swagger) | http://localhost:8000/docs |

No hace falta ninguna clave ni configuración: por defecto el asistente funciona **sin LLM** (ver [D-004](docs/DECISIONES.md#d-004--sin-llm-por-defecto-generador-detrás-de-una-interfaz)).

Para pararlo: `Ctrl + C` y después `docker compose down`.

---

## 2. Requisitos

**Opción A · Solo Docker (recomendada para probarlo):**

| Herramienta | Versión mínima | Cómo comprobarlo |
|-------------|----------------|------------------|
| Docker Desktop (o Docker Engine + plugin Compose) | Docker 24, Compose v2 | `docker --version` y `docker compose version` |
| Git | cualquiera reciente | `git --version` |

**Opción B · Desarrollo sin Docker:**

| Herramienta | Versión | Cómo instalarla |
|-------------|---------|-----------------|
| Python | 3.12 | `uv` la descarga automáticamente si no la tienes |
| uv | 0.5 o superior | `curl -LsSf https://astral.sh/uv/install.sh \| sh` (macOS/Linux) · [otras plataformas](https://docs.astral.sh/uv/getting-started/installation/) |
| Node.js | 22 LTS o superior | https://nodejs.org o `nvm install --lts` |
| npm | el que trae Node | `npm --version` |
| make | cualquiera | Viene instalado en macOS y Linux (`make --version`). En Windows, usa Docker o los comandos directos de cada sección. |

Puertos que deben estar libres: **8000** (API) y **8080** (web con Docker) o **4200** (web en desarrollo).

---

## 3. Arranque paso a paso con Docker

⏳

```bash
# 1. Construir las imágenes y arrancar ambos servicios en primer plano
docker compose up --build

# (opcional) en segundo plano
docker compose up --build -d
docker compose logs -f api      # ver los logs de la API
docker compose ps               # estado de los servicios

# 2. Comprobar que la API responde
curl http://localhost:8000/pois

# 3. Abrir la web
open http://localhost:8080      # macOS · en Linux: xdg-open · en Windows: start
```

Qué levanta `docker-compose.yml`:
- **`api`**: FastAPI con uvicorn en el puerto 8000. Lee `datos/pois.json` al arrancar, lo normaliza y escribe en el log los avisos de calidad de datos encontrados.
- **`web`**: el build de Angular servido por nginx en el puerto 8080. nginx reenvía `/api/*` a la API (sin CORS).

---

## 4. Arranque sin Docker (desarrollo)

Necesitas dos terminales.

**Terminal 1 · API**
```bash
make install                                 # crea api/.venv e instala las dependencias exactas (incluida Python 3.12 si falta)
make api                                     # http://localhost:8000 · documentación en http://localhost:8000/docs
```
Sin `make`: `cd api && uv sync --locked && uv run uvicorn app.main:app --reload --port 8000`.

Al arrancar, la API carga el catálogo y escribe en el log los avisos de calidad de datos que ha encontrado y corregido (ver `DATOS.md`).

**Terminal 2 · Web** ⏳
```bash
cd web
npm ci                                       # instala dependencias exactas del lockfile
npm start                                    # ng serve en http://localhost:4200 con proxy /api → :8000
```

Abre http://localhost:4200.

---

## 5. Tests y evaluación

El `Makefile` de la raíz agrupa los comandos habituales. `make` (sin argumentos) los lista:

```bash
make install   # dependencias exactas del backend (uv.lock)
make check     # lint + tests: lo que debe pasar antes de cada commit
make test      # solo tests
make lint      # ruff + mypy
make format    # formatea y corrige lo automático
```

Comandos equivalentes sin `make` (⏳ los que aún no existen):

```bash
# Calidad y tests del backend
cd api && uv run ruff check . && uv run mypy . && uv run pytest

# Lint y tests del frontend
cd web && npm run lint && npm test

# Evaluación del asistente con datos/evaluacion.json
# a) en proceso, sin levantar nada:
cd api && uv run python ../scripts/evaluate.py
# b) contra un servidor en marcha:
cd api && uv run python ../scripts/evaluate.py --url http://localhost:8000
```

Salida esperada de la evaluación: el resultado de cada pregunta (✅/❌ con los ids que faltan o sobran) y el total, con dos marcadores:
- **oficial**: incluye todos los `esperado_incluye` y ninguno de los `esperado_excluye`;
- **estricto**: además, no cita nada cuando la pregunta no tiene respuesta en el catálogo ([D-016](docs/DECISIONES.md#d-016--criterio-de-acierto-de-la-evaluación)).

---

## 6. Uso de la API

⏳ La referencia completa está en http://localhost:8000/docs. Ejemplos:

```bash
# Todos los puntos
curl "http://localhost:8000/pois"

# Museos accesibles, en inglés
curl "http://localhost:8000/pois?categoria=museo&accesible=true&idioma=en"

# Abiertos el lunes a las 12:00 (día ISO: 1 = lunes … 7 = domingo)
curl "http://localhost:8000/pois?abierto_en=1T12:00"

# Abiertos en una fecha y hora concretas (tiene en cuenta temporadas)
curl "http://localhost:8000/pois?abierto_en=2026-07-06T12:00"

# Un punto
curl "http://localhost:8000/pois/poi-003"

# Preguntar al asistente
curl -X POST "http://localhost:8000/preguntar" \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Voy en silla de ruedas, ¿qué museos puedo visitar?", "idioma": "es"}'
# → { "respuesta": "...", "ids": ["poi-003", "poi-015"] }
```

| Parámetro | Valores | Notas |
|-----------|---------|-------|
| `categoria` | `monumento`, `museo`, `naturaleza`, `ruta`, `gastronomia`, `servicio`, `espacio_publico` | |
| `accesible` | `true` / `false` | Los puntos sin datos de accesibilidad no aparecen con ninguno de los dos ([D-008](docs/DECISIONES.md#d-008--accesibilidad-en-tres-estados)) |
| `abierto_en` | `1T12:00` o `2026-07-06T12:00` | Formato inválido → 422 ([D-012](docs/DECISIONES.md#d-012--formato-del-filtro-abierto_en)) |
| `idioma` | `es` (por defecto) / `en` | Si falta la traducción, se devuelve el español ([D-015](docs/DECISIONES.md#d-015--idioma-con-fallback-a-español)) |

---

## 7. Configuración

⏳ Todas las variables son opcionales. Se pueden poner en un fichero `.env` en la raíz (hay una plantilla en `.env.example`).

| Variable | Por defecto | Para qué |
|----------|-------------|----------|
| `GENERADOR` | `plantilla` | `plantilla` (sin red) o `llm` |
| `LLM_API_KEY` | — | Solo si `GENERADOR=llm` |
| `ZONA_HORARIA` | `Europe/Madrid` | Zona del pueblo para "abierto ahora" y temporadas ([D-011](docs/DECISIONES.md#d-011--temporadas-se-evalúan-con-la-fecha-actual-de-madrid)) |
| `RUTA_POIS` | `datos/pois.json` | Ruta del catálogo |

---

## 8. Estructura del repositorio

```
valdelumbre-asistente/
├── api/                    Backend (FastAPI)
│   ├── app/
│   │   ├── data/           Carga del catálogo y avisos de calidad
│   │   │   └── rules/      Una regla de normalización por módulo (precio, textos, coordenadas, duplicados)
│   │   ├── domain/         Modelos, horarios (abierto_en), precio
│   │   ├── assistant/      Interpretación de la pregunta, recuperación, generadores
│   │   └── routes/         Endpoints: /pois, /pois/{id}, /preguntar
│   └── tests/
├── web/                    Frontend (Angular)
├── scripts/
│   └── evaluate.py         Pasa datos/evaluacion.json contra /preguntar
├── datos/                  Datos originales, SIN modificar
├── docs/
│   ├── DECISIONES.md       Cada decisión y su porqué
│   └── BITACORA.md         Registro cronológico del trabajo
├── .claude/                Configuración de Claude Code (ver IA.md)
│   ├── CLAUDE.md           Reglas generales del proyecto para la IA
│   ├── rules/              Reglas por área (backend, frontend, datos, documentación)
│   ├── skills/             Procedimientos repetibles
│   └── settings.json       Permisos (incluye el bloqueo de edición de datos/)
├── Makefile                Comandos del proyecto (`make` los lista)
├── docker-compose.yml
├── README.md               Este fichero
├── DATOS.md                Problemas en los datos y qué se ha hecho con cada uno
└── IA.md                   Cómo se ha usado la IA
```

---

## 9. Decisiones principales

Resumen; el detalle está en [`docs/DECISIONES.md`](docs/DECISIONES.md).

- **Monorepo** con backend y frontend: un clon y un comando ([D-001](docs/DECISIONES.md#d-001--un-único-repositorio-para-backend-y-frontend)).
- **Los datos originales no se tocan**: se normalizan al cargar, con tests y avisos ([D-003](docs/DECISIONES.md#d-003--los-datos-originales-no-se-modifican-se-normalizan-al-cargar)).
- **Sin LLM por defecto**: generador por plantillas detrás de una interfaz intercambiable ([D-004](docs/DECISIONES.md#d-004--sin-llm-por-defecto-generador-detrás-de-una-interfaz)).
- **Los hechos salen de los campos, no del texto**: accesibilidad, horario y categoría se filtran con datos estructurados, lo que neutraliza la inyección de prompt encontrada en los datos ([D-005](docs/DECISIONES.md#d-005--los-hechos-salen-de-campos-estructurados-nunca-del-texto-libre), [D-006](docs/DECISIONES.md#d-006--tratamiento-de-la-inyección-de-prompt-en-poi-013)).
- **No inventar**: los datos desconocidos (accesibilidad, horario) se muestran como tales, y si no hay respuesta en el catálogo el asistente lo dice y no cita nada.

---

## 10. Qué haría con más tiempo

*(Se completará al final.)*

---

## 11. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `port is already allocated` | El 8000 o el 8080 está ocupado | Para el proceso que lo usa (`lsof -i :8000`) o cambia el puerto publicado en `docker-compose.yml` |
| `Cannot connect to the Docker daemon` | Docker Desktop no está arrancado | Ábrelo y espera a que indique "running" |
| La web carga pero no muestra puntos | La API no está levantada o falla | `docker compose logs api` |
| `uv: command not found` | uv no está instalado o no está en el PATH | Ver [Requisitos](#2-requisitos) y abre una terminal nueva |

---

## 12. Documentación relacionada

- [`docs/DECISIONES.md`](docs/DECISIONES.md): registro de decisiones con su porqué.
- `DATOS.md`: problemas en los datos *(se redacta durante la implementación)*.
- `IA.md`: uso de la IA *(se redacta durante la implementación)*.
- [`docs/BITACORA.md`](docs/BITACORA.md): registro cronológico.
