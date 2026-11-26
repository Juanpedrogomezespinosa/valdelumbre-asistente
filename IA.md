# Cómo he usado la IA

He usado **Claude Code** (Opus 5.5) durante todo el proyecto. Este documento cuenta qué le pedí, qué acepté y, sobre todo, **qué corregí o descarté, y por qué**. Cada caso enlaza a su paso en la [bitácora](docs/BITACORA.md) o a su [decisión](docs/DECISIONES.md), donde está el detalle.

## 1. Herramienta y reglas del juego

Quería que el uso de la IA fuera **reproducible y auditable**, no un chat perdido. Por eso sus reglas están en el repositorio ([D-020](docs/DECISIONES.md#d-020--configuración-de-claude-code-dentro-del-repositorio)):

| Fichero | Qué fija |
|---------|----------|
| [`.claude/CLAUDE.md`](.claude/CLAUDE.md) | Forma de trabajar, código limpio, Git e invariantes del producto (los datos no se tocan, accesibilidad tri-estado, días ISO, citar solo lo recuperado…) |
| [`.claude/rules/`](.claude/rules/) | Reglas por área: backend, frontend, datos y documentación |
| [`.claude/skills/`](.claude/skills/) | Procedimientos repetibles: registrar una decisión, documentar un defecto de datos, evaluar el asistente y revisar la accesibilidad |
| [`.claude/settings.json`](.claude/settings.json) | Permisos: **prohibido editar `datos/`** y leer `.env`; solo comandos de calidad y tests |

**El método**, que impuse desde el principio:
1. **Proponer antes de programar.** La IA explica el plan y espera mi aprobación.
2. **Test primero** en el núcleo (normalización, horarios, interpretación de preguntas y filtros).
3. **Pasos pequeños** ([D-036](docs/DECISIONES.md#d-036--commits-pequeños-con-push-al-terminar-cada-paso-que-funciona)): cuando un paso funciona, la IA se detiene; lo reviso, hago el commit y autorizo el siguiente.
4. **Todo queda escrito:** cada paso en la bitácora y cada decisión con su porqué.
5. **Git es mío.** La IA solo puede leer el repositorio: los commits, las ramas, los merges y el push los hago yo.

También usé la IA con dos conectores: **Trello**, para mover tarjetas y marcar criterios (solo yo las paso a «Hecho»), y **Chrome**, para probar la pantalla con teclado y en distintos anchos.

## 2. Qué decidí yo y qué delegué

**Decidí yo:**
- **La arquitectura y el alcance:** un solo repositorio, datos intactos normalizados al cargar ([D-003](docs/DECISIONES.md#d-003--los-datos-originales-no-se-modifican-se-normalizan-al-cargar)), asistente sin LLM por defecto detrás de una interfaz ([D-004](docs/DECISIONES.md#d-004--sin-llm-por-defecto-generador-detrás-de-una-interfaz)), lo obligatorio primero y las mejoras después.
- **El stack y los criterios de calidad:** código en inglés, comentarios solo para el porqué ([D-022](docs/DECISIONES.md#d-022--comentarios-mínimos-solo-el-porqué)), ruff + mypy strict, TDD en el núcleo, ficheros pequeños ([D-038](docs/DECISIONES.md#d-038--ficheros-pequeños-un-módulo-por-responsabilidad)), Tailwind, Makefile y Conventional Commits.
- **El producto:** qué responde el asistente cuando no sabe ([D-032](docs/DECISIONES.md#d-032--sin-respuesta-en-el-catálogo-no-lo-sé-sin-sugerencias-ni-citas)), el diseño, el mapa, las ilustraciones y descartar el LLM.
- **Cuándo algo estaba terminado:** cada paso pasaba por mi revisión, a mano en el navegador y en `/docs`, antes del commit.

**Delegué en la IA:** la auditoría inicial de los datos (que revisé), la escritura del código y de los tests siguiendo esas reglas, la verificación automática (linters, tests y evaluación) y el borrador de la documentación.

## 3. Qué corregí o descarté, y por qué

Cada caso sigue el mismo esquema: lo que propuso o hizo la IA, por qué no lo acepté y cómo quedó.

### Correcciones al proceso

| Lo que hizo la IA | Por qué lo corregí | Cómo quedó |
|-------------------|--------------------|------------|
| Creó las reglas y las skills del proyecto **sin preguntarme** (paso 2). | Las reglas condicionan todo el desarrollo: tienen que salir de mis criterios, no de suposiciones. | Regla «preguntar antes de decidir». Revisé cada regla y cada skill; las carpetas pasaron al inglés y se añadió la sección de código limpio. |
| Propuso hacer ella el commit inicial (paso 4). | Quiero controlar el historial y revisar cada cambio antes de que entre. | Git lo gestiono yo; la IA solo lee. |
| Añadió por su cuenta un criterio en Trello: sugerir la Oficina de Turismo cuando no sabe (paso 6). | Le pedí las alternativas y su porqué. Sugerir algo no recuperado rompe la regla de citar solo lo que respalda la respuesta. | «No lo sé» a secas ([D-032](docs/DECISIONES.md#d-032--sin-respuesta-en-el-catálogo-no-lo-sé-sin-sugerencias-ni-citas)). |
| Implementó un generador con Claude, **de pago**, cuando yo solo había preguntado si era gratis (paso 14). | No había elegido proveedor. Quería algo gratuito, sin tarjeta y que el evaluador pudiera levantar sin darse de alta en nada. | Se quitó. Comparamos opciones gratuitas y elegí Ollama, local (ver más abajo). |

### Recomendaciones rebatidas o descartadas

- **SCSS frente a Tailwind** (paso 3, [D-026](docs/DECISIONES.md#d-026--estilos-con-tailwind-v4-y-tres-reglas)). La IA recomendó SCSS con tokens. Propuse Tailwind, que domino, y le pedí que justificara SCSS. Reconoció que era una preferencia y no un argumento técnico: los tokens se consiguen igual con `@theme` en Tailwind v4. Lo adopté con tres reglas: contraste AA en los tokens, componentes en lugar de `@apply` y un foco común.
- **El LLM** (paso 14, [D-048](docs/DECISIONES.md#d-048--generador-llm-opcional-y-local-ollama-con-vuelta-a-la-plantilla)). Decidí añadir un LLM como mejora opcional. Lo implementamos con un modelo local (Ollama) y lo probé con el modelo real. Escribiendo la respuesta entera, afirmó la premisa falsa de q5 («el único sitio accesible») y omitió lugares; redactando solo la introducción, inventó el nombre del pueblo. Para que no se equivocara con los datos tuvo que quedarse en una primera frase vigilada, y así aportaba muy poco: al probarlo vi que era «lo mismo que antes». Darle un papel útil, que es interpretar preguntas fuera del vocabulario cerrado, requería más tiempo del que tenía antes de la entrega para hacerlo bien. **Preferí no entregar algo a medias**: lo descarté y dejé el asistente basado en reglas, que es predecible y pasa la evaluación. El código queda en el historial (`bdae57e`).
- **Un campo `puntos` en `/preguntar`** (paso 9.1, [D-042](docs/DECISIONES.md#d-042--preguntar-devuelve-solo-respuesta-e-ids)). La IA lo propuso para ahorrar peticiones a la pantalla. Con mi pauta de seguir el enunciado al pie de la letra, lo descartó ella misma: el contrato es `{respuesta, ids}`.
- **Fotos de stock y enlaces a mapas reales** (paso 13, [D-046](docs/DECISIONES.md#d-046--ilustración-por-categoría-y-ubicación-relativa-en-lugar-de-fotos-y-enlaces-a-mapas)). Quería imágenes en la ficha y cómo llegar a cada punto. Al revisar los datos vimos que no hay imágenes y que las coordenadas caen en el centro de Madrid. Una foto de stock o un enlace a Google Maps habrían engañado al turista, así que elegí una ilustración por categoría y una ubicación relativa («a 120 m al oeste de la Plaza Mayor»).

### Fallos que encontré yo al revisar

Los tests de la IA estaban en verde en todos estos casos. Los encontré probando a mano.

| Qué vi | Paso | Qué se hizo |
|--------|------|-------------|
| `/docs` anunciaba un formato de error 422 que la API no devuelve. | 8.4 | Esquema de error real y tests sobre `/openapi.json`. |
| El ejemplo de error de `/docs` hablaba de `categoria` en rutas que no tienen ese parámetro. | 9.3 | Un ejemplo por ruta, generado con los mensajes reales. |
| La página saltaba a la derecha al aparecer la barra de scroll. | 12 | `scrollbar-gutter: stable`. |
| En móvil, el paisaje cortaba el castillo y dejaba fuera el sol. | 12.1 | Composición propia para móvil. |
| El primer mapa: «queda muy cutre» y «no puede moverse con el ratón». | 13.1 | Mapa nuevo con arrastre, zoom, teclado y vista Lista / Mapa ([D-047](docs/DECISIONES.md#d-047--mapa-interactivo-con-vista-lista--mapa)). |
| «¿Hay wifi en el parque?» respondía con el parque, como si fuera un sí. | 16 | El asistente dice lo que no consulta y da el precio de cada lugar. |

**Lección:** los tests de comportamiento no ven el contrato publicado ni la pantalla. En los dos fallos de `/docs`, la corrección incluyó tests sobre `/openapi.json` para que no volvieran a pasar.

## 4. Qué le pedí

| Fase | Lo que le pedí |
|------|----------------|
| Antes del código | Auditar los datos y la evaluación, y proponer una arquitectura **sin escribir código**. |
| API y datos | Cada regla de normalización y cada endpoint con test primero, en pasos que yo revisaba. |
| Asistente | Interpretación por reglas, citas solo de lo recuperado y un script de evaluación con un criterio estricto propio. |
| Pantalla | Accesible de verdad: teclado, lector de pantalla y contraste comprobado, no solo «etiquetas puestas». |
| Antes de entregar | Que contrastara el proyecto con cada línea del enunciado, que comprobara «todas las preguntas posibles» y que buscara «todos los bugs posibles». |

## 5. Qué acepté, y con qué control

- **Los planes por rama y por paso**, después de revisarlos y ajustarlos.
- **El código con test primero.** Se aceptaba con `make check` en limpio (ruff, mypy strict, angular-eslint y tests) y tras mi prueba a mano.
- **La auditoría de los datos.** Incluida la deducción de los días ISO a partir de q3, que quedó fijada con un test ([DATOS.md](DATOS.md)).
- **La batería de preguntas como test permanente** (`api/tests/test_assistant_battery.py`). La acepté después de comprobar que detecta fallos al estropear la búsqueda a propósito.
- **Los avisos de seguridad de la IA**, como el de que el enlace de invitación de Trello daba acceso de edición: lo cambié por el tablero público en solo lectura.

## 6. Lo que la IA corrigió sola antes de entregarme un paso

Formaba parte del método: revisar su propio trabajo antes de pararse.
- Sustituyó un `# type: ignore` por la forma tipada de FastAPI, en lugar de silenciar a mypy (paso 8.3).
- Un mensaje de error habría mostrado «Valores posibles: .» vacío (paso 8.3).
- Eliminó un test de relleno que no comprobaba nada (paso 9.2).
- «Is there any zipline adventure park?» citaba el aparcamiento («Cuesta Car Park»). Ahora una palabra solo nombra un lugar si aparece en un único nombre ([D-051](docs/DECISIONES.md#d-051--un-lugar-nombrado-manda-y-las-palabras-comunes-no-nombran-lugares)).
- Detectó que su arreglo de «cuesta» había roto «Tell me about Cuesta Car Park» porque repetía la batería entera tras cada cambio (paso 16).

## 7. Cómo se buscaron los fallos

**Lo que hice yo:** probar a mano cada paso con pantalla o `/docs`; releer el enunciado línea a línea y convertir cada línea en una pregunta de verificación (¿responde a cualquier pregunta o solo a las de la evaluación?, ¿el mapa se usa con teclado y lector?, ¿hay demasiados tests?); pedir explícitamente la caza de fallos, y hacer el recorrido final con VoiceOver.

**Lo que hizo la IA con cada petición:**
- **Responder con datos, no de memoria:** antes de contestar si el asistente respondía a cualquier pregunta, probó 9 que no estaban en la evaluación.
- **Convertir «todas las preguntas posibles» en algo comprobable:** 166 combinaciones de filtros comparadas con `GET /pois`, los 17 lugares por nombre, trampas e inyecciones, parámetros raros en la API y recorridos en Chrome.
- **Investigar antes de arreglar:** «monumentos accesibles → no tengo información» parecía un fallo de búsqueda, pero era un mensaje engañoso, porque no hay monumentos accesibles.
- **Buscar la familia del fallo**, no solo el caso: tras «cuesta», revisó todas las palabras que nombran lugares y encontró seis más.

## 8. Límites de la herramienta

- **El clasificador de seguridad de Claude Code** no dejó que la IA creara su propio fichero de permisos hasta que lo autoricé de forma explícita. Me parece razonable.
- **El bloqueo de Git** que pedí funcionó también contra ella: intentó un `git rm` y se le impidió.
- **El conector de Trello** no permite poner nombre a las etiquetas (las nombré a mano) y guardaba `<` y `>` como entidades HTML.
- **Lo que no puede hacer:** escuchar un lector de pantalla. El recorrido con VoiceOver lo hice yo.

## 9. Conclusiones

- **Las reglas escritas no evitan todos los errores, pero los hacen fáciles de corregir.** Aun con la regla de preguntar antes de decidir, la IA implementó Claude sin que yo lo hubiera elegido. Como la regla estaba escrita, la corrección fue inmediata y no hubo nada que discutir.
- **Revisar a mano sigue siendo imprescindible.** Los seis fallos de la tabla del apartado 3 convivían con todos los tests en verde; los encontré mirando la pantalla y `/docs`.
- **Pedir el porqué cambia la respuesta.** La recomendación de SCSS y el criterio de la Oficina de Turismo no resistieron la pregunta «¿por qué?».
- **Descartar también es decidir.** El LLM funcionaba, pero no aportaba lo suficiente para justificar su riesgo. Preferí un asistente predecible y bien probado.
