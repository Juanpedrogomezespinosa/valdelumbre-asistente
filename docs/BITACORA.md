# Bitácora de la prueba técnica · Valdelumbre

Registro cronológico de mi trabajo: qué hice en cada paso, **por qué** y cómo lo verifiqué.

**Forma de trabajar.** Yo dirijo: fijo los criterios, tomo las decisiones y reviso cada paso antes de hacer el commit. Claude Code (la IA) propone y, cuando lo apruebo, programa con test primero. Las decisiones están en [`DECISIONES.md`](DECISIONES.md); los defectos de datos, en [`DATOS.md`](../DATOS.md), y el uso de la IA, en [`IA.md`](../IA.md). Los ficheros concretos de cada paso están en el historial de git.

---

## Paso 0 · Auditoría inicial, sin código — 2026-11-24

**Antes de escribir código**, pedí a la IA que auditara el enunciado, `datos/pois.json` (18 puntos) y `datos/evaluacion.json` (6 preguntas), y que propusiera una arquitectura.

### 0.1 Defectos en los datos
Encontramos 11 defectos (D1–D11): un registro duplicado, una instrucción inyectada para el asistente, coordenadas invertidas, precios en formatos distintos, accesibilidad y horarios desconocidos, una temporada, días de la semana sin documentar, tildes incoherentes, traducciones vacías y avisos importantes solo en el texto libre. Cada uno, con su riesgo y su tratamiento, está en [`DATOS.md`](../DATOS.md).

Destaco la deducción de los días: la pregunta q3 (lunes a las 12:00) excluye poi-003 (días 2–7) e incluye poi-001 (días 1–6), así que **1 = lunes y 7 = domingo** (ISO 8601).

### 0.2 Qué evalúa en realidad `evaluacion.json`

| Id | Pregunta | Qué evalúa |
|----|----------|------------|
| q1 | Silla de ruedas + museos | Filtro estructurado de accesibilidad y categoría. Trampas: poi-013 (se declara accesible en una inyección) y poi-004 (duplicado). |
| q2 | *Kids outdoors* (inglés) | Multilingüe y sinónimos. |
| q3 | Abierto lunes 12:00 | Horarios, días ISO y `always_open`. |
| q4 | Probar vino | Recuperación por etiqueta o sinónimo. |
| q5 | «¿El único sitio accesible?» | Premisa falsa más inyección. |
| q6 | Tirolina | Fuera del catálogo: no inventar. |

**Conclusión:** la evaluación premia los filtros estructurados, las citas y la resistencia a la inyección, no la calidad de un modelo. Un recuperador determinista bien hecho puede acertar 6/6 sin LLM. El criterio del JSON da q6 por buena siempre (listas vacías), así que el script añadiría un criterio estricto: sin citas cuando no hay nada.

### 0.3 Arquitectura
- **Principio rector:** los datos originales no se tocan; se normalizan **al cargar**, en una única capa probada que genera avisos.
- **Asistente:** interpretar la pregunta con reglas → filtrar con los mismos campos que `GET /pois` → puntuar y aplicar un umbral («no lo sé» si nada lo supera) → generar con una interfaz que admite plantilla o LLM.
- **API:** `GET /pois` con `categoria`, `accesible`, `abierto_en` (`<día ISO>T<HH:MM>`) e `idioma`; `GET /pois/{id}`; `POST /preguntar`.
- **Pantalla:** asistente, listado con filtros, ficha y mapa opcional, con HTML semántico y comprobación con teclado y VoiceOver.

### 0.4 Decisiones de partida
Aprobé: generador por plantilla por defecto y LLM opcional detrás de una interfaz (P1); excluir el duplicado poi-004 con un 404 (P2); evaluar las temporadas con la fecha actual de Madrid (P3); copiar los JSON sin cambios dentro del repositorio (P4), y Python 3.12 con `uv`, Angular estable y Docker Compose (P5). Quedan en `DECISIONES.md` (D-001 a D-020).

---

## Paso 1 · Andamiaje del repositorio y documentación base — 2026-11-24
- **Un único repositorio** para backend y frontend (D-001), con `datos/` copiado sin cambios y verificado con SHA-1.
- `DECISIONES.md` con formato fijo (Contexto / Decisión / Por qué / Alternativas / Consecuencias) y un `README.md` de arranque en el que los comandos aún no implementados llevan la marca ⏳.
- **La configuración de la IA se versiona** (D-020): `CLAUDE.md`, reglas por área en `.claude/rules/` y cuatro skills en `.claude/skills/`. Así quien evalúe puede ver qué restricciones tenía.
- El clasificador de seguridad de Claude Code impidió que la IA creara su propio fichero de permisos (`.claude/settings.json`). Lo resolví en el paso 3.

**Por qué este orden:** fijar las reglas antes de programar permite contrastar cada paso con ellas y deja el uso de la IA acotado y auditable.

---

## Paso 2 · Corrección de rumbo: preguntar antes de configurar — 2026-11-24
**Qué pasó:** en el paso 1, la IA creó las reglas y las skills sin preguntarme antes. La corregí: las reglas condicionan todo el desarrollo, así que deben salir de mis criterios y no de suposiciones de la IA.

**Qué fijé:**
- La IA **me pregunta antes** de crear o cambiar cualquier configuración, regla o convención.
- **Código limpio y solo los comentarios necesarios:** un comentario explica un *porqué* no evidente, nunca lo que ya dice el código. Sobrecomentar es un defecto típico del código generado por IA, y lo reviso en cada paso.
- Las reglas y skills del paso 1 se revisan con mis criterios: se mantienen, se ajustan o se eliminan.

| Tema | Lo que decidí | Decisión |
|------|---------------|----------|
| Idioma del código | Inglés; los campos del JSON y de la API se mantienen | D-021 |
| Comentarios | Solo el porqué; docstring solo en la interfaz pública no trivial | D-022 |
| Calidad automática | ruff + mypy strict + angular-eslint/Prettier | D-023 |
| Tests | TDD en el núcleo | D-024 |
| Git | Conventional Commits en español, una rama por bloque | D-025 |
| Errores de la API | En el idioma pedido (es/en) | D-021 |

Resultado de la revisión: se mantienen las cuatro skills (dos ajustadas a las nuevas rutas), `CLAUDE.md` se reescribe y las carpetas pasan al inglés (`api/app/{data,domain,assistant,routes}`).

---

## Paso 3 · Permisos y decisiones del frontend — 2026-11-24
- **`.claude/settings.json`:** autoricé de forma explícita a la IA a crearlo. Bloquea la edición de `datos/` y la lectura de `.env`, y permite solo los comandos de calidad y tests.
- **Estilos:** la IA recomendó SCSS; **propuse Tailwind** y le pedí que justificara SCSS. Reconoció que su recomendación era una preferencia y no un argumento técnico. Adopté Tailwind v4 con tres reglas: tokens de color con contraste AA, componentes en lugar de `@apply` y un foco común (D-026).
- El resto de decisiones: rutas `/`, `/pois` y `/pois/:id` (D-027), diccionario de idiomas propio con signals (D-028), tests con el runner del CLI y Testing Library (D-029), aspecto sobrio y cálido con modo oscuro (D-030), tarjetas con resumen y enlace (D-031) y mapa SVG solo si daba tiempo (D-019).

Con esto cerré las decisiones previas al código (D-001 a D-031).

---

## Paso 4 · Git en mis manos — 2026-11-24
- La IA había propuesto hacer el commit inicial. **Decidí encargarme yo de todo Git** (commits, ramas, merges y push) para mantener el control del historial; la IA solo puede leer el estado del repositorio.
- `.gitignore` completado. Versiono a propósito `.claude/`, los lockfiles (builds reproducibles), `datos/`, `.env.example` y los documentos de `docs/`, que forman parte de la entrega.

---

## Paso 5 · Raíz limpia — 2026-11-24
- Quise que en la raíz estuvieran solo los tres documentos que pide el enunciado (`README.md`, `DATOS.md` e `IA.md`).
- `DECISIONES.md` y `BITACORA.md` pasan a `docs/` y `CLAUDE.md` a `.claude/`, con todas las referencias actualizadas.

---

## Paso 6 · Tablero de Trello — 2026-11-24
**Tablero:** https://trello.com/b/V7dKvO5a/valdelumbre

- **Mis criterios:** columnas Backlog · Por hacer · En curso · Revisión · Hecho, donde «Revisión» es el momento en que reviso lo hecho antes del commit; una historia por funcionalidad («Como… quiero… para…») con criterios de aceptación en un checklist; etiquetas por área, y cada tarjeta con sus decisiones y su rama.
- **Contenido:** 12 historias (H1–H12; el mapa y el LLM, opcionales) y 4 tareas técnicas (T1–T4), que la IA creó con el conector de Trello.
- **Flujo:** la IA mueve las tarjetas a «En curso» y a «Revisión» y marca los criterios; **solo yo las paso a «Hecho»**.
- **Mi revisión:**
  - La IA había añadido tres criterios por su cuenta. Aprobé dos (una inyección sintética en H9 y el código de salida del script en T2) y **rechacé el tercero** (en H8, sugerir la Oficina de Turismo): ante una pregunta sin respuesta en el catálogo, «no lo sé» a secas (D-032).
  - Para enlazar el tablero, la IA advirtió de que la URL de invitación da acceso de edición a cualquiera. Lo hice público en solo lectura y enlazo la URL normal.
- Límites del conector: no permite poner nombre a las etiquetas (las nombré a mano) y guarda `<` y `>` como entidades HTML (se reescribieron esos criterios).

---

## Paso 7 · `feat/api-data`: dominio y capa de datos — 2026-11-24
**Aprobé el plan**, en 7 pasos guiados por tests. Decisiones de diseño: D-033 (JSON crudo con pydantic y dominio con dataclasses), D-034 (cierre exclusivo; las franjas que cruzan la medianoche se descartan), D-035 (una categoría desconocida detiene la carga) y **D-036: pasos pequeños**. Cuando un paso funciona, la IA se detiene hasta que lo reviso y hago el commit.

### 7.1 · Proyecto Python
- Python 3.12 con `uv` (`uv.lock` versionado), ruff, mypy `strict` y pytest.
- Primer test: la huella SHA-1 de `datos/*.json` demuestra que los datos siguen intactos (D-003).

### 7.2 · Comandos con make
- Comparé las opciones para agrupar los comandos (Makefile, npm scripts, poethepoet o nada) y **elegí un Makefile en la raíz** (D-037). Cada comando se añade cuando existe y funciona.

### 7.3 · Horarios
- TDD (25 casos): siempre abierto, horario desconocido → `None` (D-009), días ISO con un test que reproduce la deducción de q3 (D-010), franjas partidas, cierre exclusivo y temporadas que cruzan el año (D-011).
- La fecha de referencia para las temporadas la pasa quien llama, así que el dominio no depende del reloj.

### 7.4 · Precio
- `Price` con `Decimal` (importes exactos). Se normalizan números, «gratis»/«free», «4,5» y rangos («25-35»); `null` es desconocido sin aviso, y cualquier otro valor, desconocido **con aviso** (D-014).

### 7.5 · Textos: traducciones vacías e instrucciones inyectadas
- Una traducción vacía pasa a «sin texto» con aviso, y el inglés que falta se sirve en español marcado (D-015).
- Las frases con instrucciones dirigidas al asistente se eliminan y se conserva el resto (D-006). Tests con la inyección real, una sintética en inglés y dos textos legítimos que no deben confundirse con una inyección. Sobre el catálogo real, sin falsos positivos.

### 7.6 · Coordenadas invertidas
- Hallazgo: las coordenadas invertidas de poi-011 son **válidas por sí solas**; el error solo se ve comparando con el resto. La regla usa la mediana del catálogo, que un único punto erróneo no puede desplazar, e intercambia el punto si solo encaja al revés (D-013).

### 7.7 · Duplicados
- Dos fichas son la misma si coinciden el nombre (sin tildes ni mayúsculas) y las coordenadas a unos 11 m. Se conserva la más completa (D-007).

### 7.8 · Una regla por módulo
- `normalization.py` llegó a 218 líneas con cuatro reglas. **Fijé como norma los ficheros pequeños**, uno por responsabilidad (D-038), y se dividió en `api/app/data/rules/` sin cambiar el comportamiento: los 76 tests siguieron pasando.

### 7.9 · Carga del catálogo
- `load_catalog()` valida el JSON, aplica las reglas y devuelve los puntos y los avisos. Un aviso solo se emite cuando algo **se corrige, se descarta o puede malinterpretarse**: un horario vacío sí (parece «cerrado» y no lo es); un `null` explícito no.
- Sobre el catálogo real: 17 puntos servidos y 7 avisos, que coinciden con la auditoría del paso 0.
- Verificado: `make check` limpio, 91 tests.

---

## Paso 8 · `feat/api-routes`: la API — 2026-11-24 y 25
Fusioné `feat/api-data` y aprobé el plan: filtrado en el dominio, reutilizable por `/preguntar`; textos ya en el idioma pedido; reloj inyectado; catálogo cargado una vez al arrancar.

### 8.1 · Arranque
- La API carga el catálogo al arrancar y escribe en el log el resumen y cada aviso de datos. `make api`.
- Starlette recomienda sustituir `httpx` en los tests. **Decidí mantener `httpx`**, que funciona, en lugar de añadir un paquete nuevo con la entrega cerca.
- Trello: H1 → «Revisión».

### 8.2 · `GET /pois/{id}`
- Respuesta en el idioma pedido, con el idioma real de cada texto, accesibilidad y «abierto ahora» con tres estados, horario y precio como datos y como texto («4,50 €» / «€4.50»).
- 404 con mensaje en el idioma pedido, también para el duplicado descartado.

### 8.3 · `GET /pois` con filtros
- Decisiones que aprobé: errores 422 en el idioma pedido (D-039), `abierto_en` interpretado en hora de Madrid (D-012) y respuesta como lista.
- Tests contra el catálogo real: q3, la temporada de poi-014 (cerrado en noviembre y abierto en julio), poi-013 fuera de `accesible=true` aunque su descripción diga lo contrario y poi-004 ausente.
- La IA corrigió dos cosas propias antes de entregarme el paso: un `# type: ignore` que sustituyó por la forma tipada de FastAPI, y un mensaje de error que habría mostrado «Valores posibles: .» vacío.
- Verificado: `make check` limpio, 145 tests.

### 8.4 · Los errores documentados en `/docs`
- **Lo detecté en mi prueba manual:** `/docs` seguía anunciando el 422 por defecto de FastAPI, pero la API responde `{"detail": "<mensaje>"}`, y el 404 no estaba documentado.
- Corregido con test primero sobre `/openapi.json`. Lección: un cambio en el formato de respuesta se comprueba también en el contrato publicado, no solo en los tests de comportamiento.

---

## Paso 9 · `feat/assistant`: el asistente — 2026-11-25
Fusioné `feat/api-routes` después de probar la API a mano (14/14 comprobaciones). **Mi pauta para este bloque:** la IA decide lo técnico siempre que se siga el enunciado al pie de la letra, y lo anota todo.

### 9.1 · Interpretación de preguntas
- Un módulo por señal (accesibilidad, categorías, temas, día y hora, «el único»), con test primero y uno de composición con las seis preguntas de la evaluación (D-040, D-041).
- Siguiendo esa pauta, la IA descartó su propia propuesta de añadir un campo `puntos` a la respuesta: el contrato es `{respuesta, ids}` (D-042).

### 9.2 · Recuperación, generador y servicio
- Interpretar → recuperar → generar, y descartar al final cualquier id no recuperado (D-043). Las seis preguntas de la evaluación: 6/6, también con el criterio estricto.
- Fallos detectados por los tests y corregidos:
  - «¿es accesible el castillo?» devolvía *otros* lugares accesibles: los nombres se buscan ahora en todo el catálogo;
  - «Is there any zipline adventure park?» citaba el aparcamiento («Cuesta Car Park»): una palabra solo nombra un lugar si aparece en un único nombre;
  - un test esperaba «no accesible» de un punto sin datos, y otro no comprobaba nada (se eliminó).

### 9.3 · `POST /preguntar`
- Contrato estricto del enunciado: `{pregunta, idioma}` → `{respuesta, ids}`, sin más campos. Pregunta de 1 a 500 caracteres; 422 en el idioma pedido.
- **Lo detecté en `/docs`:** el ejemplo del 422 hablaba de `categoria` también en rutas que no tienen ese parámetro. Ahora cada ruta tiene su ejemplo, generado con las mismas funciones que los mensajes reales. Con test.
- Verificado: `make check` limpio, 260 tests.

### 9.4 · Script de evaluación
- `scripts/evaluate.py`: en proceso por defecto o contra un servidor con `--url`; marcador oficial y estricto (D-016); código de salida 0, 1 o 2. La evaluación completa queda también como test de regresión.
- Al probarlo a mano se corrigieron el informe enterrado bajo los logs y la traza de Python con el servidor apagado.
- `make eval` → Oficial 6/6 · Estricto 6/6, en proceso y contra el servidor.
- Trello: T2, H8 y H9 → «Revisión».

---

## Paso 10 · `feat/web`: la pantalla — 2026-11-25
Fusioné `feat/assistant`. Al preparar el plan, la IA detectó una contradicción entre D-031 y D-043 (si el asistente usa las descripciones); decidí mantener D-043.

### 10.1 · Andamiaje y estructura común
- Angular 22 standalone, sin zone.js, con Tailwind v4, TypeScript `strict`, angular-eslint y Testing Library. Proxy de desarrollo `/api` → API.
- **Contraste WCAG calculado** para cada par de colores en los dos temas; el anillo de foco se separa 2 px para que nunca quede sobre el botón.
- Estructura común: «saltar al contenido», navegación con `aria-current`, selector de idioma que cambia `<html lang>` al momento, título de pestaña por página y foco en el `<h1>` tras cada navegación.
- Se desactivó la pregunta de estadísticas del CLI, que bloquearía un arranque sin terminal interactiva (Docker o el evaluador).

### 10.2 · Listado `/pois`
- Filtros en la URL (el botón Atrás deshace un cambio). `accesible=false` es «solo no accesibles» y los puntos sin datos solo aparecen sin filtro (D-008). «Abierto ahora» envía la hora real, que la API convierte a Madrid.
- Una región `role="status"` anuncia la carga y el número de resultados. La tarjeta da siempre los estados en texto.
- Trello: H2, H3 y H4 → «Revisión».

### 10.3 · Ficha `/pois/:id`
- Horario en palabras («martes a domingo», «del 1 de junio al 30 de septiembre») o «Horario no disponible: consulta en la Oficina de Turismo» (D-009). `lang` en cada texto servido en otro idioma.
- Un punto inexistente da «Este punto no existe en el catálogo», distinto de un error de carga.
- Trello: H5 y H6 → «Revisión».

### 10.4 · Pantalla del asistente `/`
- **Decidí** terminar primero lo obligatorio y dejar el LLM opcional (H12) para el final, si daba tiempo.
- Formulario con etiqueta y pista, respuesta en una región anunciada y, fuera de ella, las tarjetas de los puntos citados. La respuesta se muestra como una lista de verdad para que el lector anuncie cuántos lugares hay.
- La IA corrigió al repasar la plantilla un nivel de encabezado repetido en las tarjetas citadas.
- Trello: H7 → «Revisión».

### 10.5 · Revisión de accesibilidad
- Checklist de la skill `revisar-accesibilidad` y recorrido real con teclado en Chrome.
- Corregido con test primero: el error de la pregunta no quedaba ligado al campo (ahora `aria-invalid` y `aria-describedby`), y el selector de idioma podía mostrar el idioma equivocado al arrancar.
- Sin scroll horizontal a 320 px.

---

## Paso 11 · Docker Compose — 2026-11-25
- `docker compose up --build` (o `make up`): web en http://localhost:8080 y API en http://localhost:8000. nginx sirve la web y reenvía `/api/`.
- `datos/` se monta **en solo lectura**: el invariante «los datos no se modifican» lo garantiza también el sistema de ficheros.
- Verificado: los dos contenedores *healthy*, 17 puntos, rutas de Angular al recargar, 422 en inglés, los 7 avisos en el log, escritura en `/datos` rechazada y `make eval` contra Docker en 6/6. Repetido desde un clon limpio de GitHub.

---

## Paso 12 · Rediseño «guía editorial» — 2026-11-25
- Con lo obligatorio terminado, **revisé la pantalla y pedí un diseño menos genérico**. También detecté que, en `/pois`, la página saltaba a la derecha al aparecer la barra de scroll.
- La IA propuso tres direcciones con maquetas; **elegí la guía editorial**, con fuentes propias servidas desde la app (D-044).
- Cambios: `scrollbar-gutter: stable` (corrige el salto), Fraunces y Source Sans 3, paleta papel/terracota/oliva con contraste comprobado en los dos temas (0 fallos), portada con un paisaje SVG decorativo, sugerencias de pregunta comprobadas contra la API y tarjetas clicables que siguen siendo una sola parada de tabulación.

### 12.1 · Paisaje en móvil, favicon y botón de tema
- **Detecté** que en móvil el paisaje cortaba el castillo y dejaba fuera el sol, y pedí un favicon y un botón de tema claro/oscuro.
- Composición propia para móvil, favicon de castillo y botón de tema con `aria-pressed` que recuerda la elección (D-045).

---

## Paso 13 · Mapa del pueblo, ilustraciones y ubicación — 2026-11-25
- Pedí el mapa (H11) y propuse imágenes en la ficha y cómo llegar a cada punto. Al revisar los datos vimos que el catálogo no trae imágenes y que las coordenadas caen en el centro de Madrid. **Descarté las fotos de stock y los enlaces a mapas externos**, porque serían engañosos, y elegí una ilustración por categoría y una ubicación calculada desde las coordenadas (D-046).
- TDD en las funciones puras: distancias, rumbo, encuadre y frases como «A 120 m al oeste de Plaza Mayor».

### 13.1 · Mapa interactivo con vista Lista / Mapa
- **Rechacé el primer mapa:** «queda muy cutre» y «no es accesible, no puede moverse con el ratón». Cumplía lo mínimo (enlaces con nombre), pero no se podía desplazar ni ampliar y el centro quedaba apiñado.
- La IA hizo un mapa nuevo sin librería y **elegí** pestañas Lista / Mapa (D-047).
- TDD del núcleo (zoom, límites, centrado). Arrastre, rueda proporcional, pellizco, botones y teclado (flechas, + − y 0); marcadores con el icono de su categoría y una tarjeta anunciada al elegirlos.
- Verificado en Chrome con ratón y teclado, y sin scroll horizontal a 320 px.

---

## Paso 14 · El LLM opcional (H12): lo probé y lo descarté — 2026-11-25
- **Primer intento, que corregí:** la IA implementó un generador con Claude, de pago, cuando yo solo había preguntado si era gratis. La paré: no había decidido proveedor y quería algo **gratuito, sin tarjeta y fácil de levantar para el evaluador**.
- La IA comparó opciones gratuitas (Gemini, Groq y Ollama) y **elegí Ollama dentro de Docker Compose**: sin cuenta, sin clave y sin tarjeta para nadie.
- **Prueba real con el modelo.** Escribiendo la respuesta entera, el modelo afirmó la premisa falsa de q5, omitió lugares e inventó texto. Tras dos rediseños (el LLM solo redacta la introducción, el código pone la lista y los ids, y una comprobación rechaza nombres propios inventados) llegó a 6/6, pero solo cambiaba la primera frase.
- **Mi decisión:** al probarlo me pregunté qué aportaba, «porque es lo mismo que antes». Darle un papel útil, que es interpretar preguntas fuera del vocabulario cerrado, requería más tiempo del que quedaba para hacerlo bien. **Preferí no entregar algo a medias** y lo descarté: «si vamos a hacerlo mal, prefiero no meter LLM» (D-048 ❌).
- Se quitó todo el código y la configuración del LLM; queda en el historial (`bdae57e`). Verificado: 270 tests y la evaluación en 6/6.

---

## Paso 15 · Respuestas vacías que dicen por qué — 2026-11-25
- **Repasé el enunciado** y lo convertí en preguntas de verificación: si el asistente responde a cualquier pregunta o solo a las de la evaluación, si el mapa se usa con teclado y lector, si hay demasiados tests y si el script de evaluación está hecho.
- La IA probó 9 preguntas que no están en la evaluación: 5 bien, 3 mejorables y 1 fuera del vocabulario. «Quiero ver monumentos que sean accesibles» parecía un fallo, pero la búsqueda era correcta (no hay monumentos accesibles): lo engañoso era el mensaje.
- **Aprobé la mejora** (D-049): una respuesta vacía dice si ningún lugar cumple lo pedido («museo · abierto el lunes») o si no se entendió la pregunta. Contrastado con `GET /pois`.

---

## Paso 16 · Batería de preguntas y caza de fallos — 2026-11-25
- **Pedí** «comprobar todas las preguntas posibles» y «buscarle todos los bugs posibles antes de entregarlo», y encontré un fallo: «hay wifi en el parque?» respondía con el parque, como si la respuesta fuera sí.
- **Método.** Las preguntas posibles son infinitas, así que se recorrió de forma sistemática el vocabulario que entiende el asistente:
  1. **Filtros:** 166 combinaciones de tipo de lugar, accesibilidad y momento, en los dos idiomas, comparadas con `GET /pois`. 0 discrepancias.
  2. **Nombres:** los 17 lugares con tres preguntas cada uno, más nombres cortos.
  3. **Temas:** 22, revisados a mano.
  4. **Preguntas de turista y trampas:** 40, entre ellas inyección, SQL, `<script>`, emojis y horas imposibles. Ninguna cita un id fuera del catálogo.
  5. **API:** 46 parámetros y cuerpos raros. Ningún error 500.
  6. **Web en Chrome:** idioma, recarga, rutas inexistentes, botón Atrás, consola limpia y sin scroll horizontal a 320 y 375 px.
- **Corregido con test primero** (D-050, D-051):
  - el wifi y lo que el asistente no consulta (mascotas, aseos, pago, reservas…), que ahora lo dice;
  - «¿Qué monumentos son gratis?» listaba monumentos de pago sin decirlo: ahora cada línea lleva el precio;
  - «¿Dónde se come bien?» no se entendía;
  - «No tengo información» ahora dice qué se puede preguntar;
  - un lugar nombrado manda sobre los demás;
  - «¿Cuánto cuesta el castillo?» citaba el Aparcamiento de la Cuesta, y palabras como main, centro o mayor nombraban lugares;
  - el arreglo de «cuesta» rompió «Tell me about Cuesta Car Park»; la batería lo detectó y se afinó.
- **Limitaciones que quedan** (en el README): vocabulario cerrado («un día de lluvia»), «Is there a car park?», «a las 25:00» se ignora, un número en `pregunta` da el mensaje de «vacía» y la lista de lo que no se consulta es cerrada.
- **La batería queda como test** (`api/tests/test_assistant_battery.py`, que aprobé): 11 tests, sin red y en algo más de un segundo. Las 166 combinaciones van en un solo test para no inflar el recuento, porque había preguntado si había demasiados. Se comprobó que **detecta fallos de verdad** estropeando la búsqueda a propósito.
- Verificado: `make check` limpio (327 tests del backend y 91 de la web) y la evaluación en 6/6.

---

## Paso 17 · Arranque desde un clon limpio — 2026-11-25
- La prueba que hará el evaluador: clon de `main` desde GitHub y `docker compose build --no-cache`.
- Resultado: servicios *healthy*, 17 puntos, rutas al recargar, `/api/preguntar` responde, `make eval` contra Docker en 6/6 · 6/6 y fuentes servidas desde la app, sin URLs externas.

---

## Paso 18 · Repaso de verificación — 2026-11-25
- **Pedí un repaso más** antes de documentar, y **decidí** que las coordenadas se quedan tal como vienen en los datos.
- Repaso: sin código muerto, sin textos sin usar, sin restos del LLM, los 41 comentarios explican un *porqué*, dos anclas rotas corregidas y ningún secreto en git.
- `make check` limpio (327 + 91 tests) y `make eval` en 6/6.

---

## Paso 19 · Teclado y lector de pantalla — 2026-11-25
- **Pedí confirmar** que toda la web se usa solo con teclado y con lector de pantalla.
- Recorrido real con teclado en Chrome y auditoría de lo que lee el lector en 7 pantallas: un solo `<h1>`, sin saltos de nivel, las cuatro regiones, ningún control sin nombre, ningún SVG que se lea por error y orden de tabulación lógico con foco visible.
- **Corregido con test primero:**
  1. al cambiar un filtro o la vista, el foco saltaba al `<h1>` y quien usa teclado perdía su sitio;
  2. al tabular a un marcador fuera de la vista, el navegador desplazaba el interior del mapa; ahora es la vista la que se centra en el marcador (17 de 17 se ven enteros).
- Descartado como fallo: un `<div>` que recibía el foco al final lo inyecta la extensión de Chrome de la IA, no la app.
- **Hice el recorrido con VoiceOver** sin encontrar problemas.
- Verificado: `make check` limpio (327 tests del backend y 93 de la web).

---

## Paso 20 · Documentos de entrega — 2026-11-26 (rama `docs/entrega`)
- `DATOS.md`: los 12 defectos (D1–D12) con su riesgo, su tratamiento y el test que lo cubre.
- Depuré esta bitácora: quité las notas de trabajo y los detalles que ya están en git, la pasé a primera persona y corregí una incoherencia sobre quién eligió Claude en el paso 14. Los hechos no cambian.
- `IA.md`: qué pedí, qué acepté y qué corregí o descarté, con cada caso enlazado a su paso o a su decisión.
- `README.md` final: arranque en 3 pasos con Docker (con Git o con ZIP), qué probar, tecnologías y por qué, decisiones, proceso con Trello, limitaciones, qué haría con más tiempo y desarrollo sin Docker.
- Al verificar el README encontré dos fallos en la instalación, que corregí:
  - `web/.nvmrc` decía solo `22`, y `nvm use` podía elegir un Node 22 anterior al mínimo de Angular (22.22.3). Ahora fija la versión exacta, `22.23.5`, y el README dice `nvm install`.
  - El comando para evaluar con Docker no funcionaba, porque el contenedor de la API no incluía `scripts/`. `docker-compose.yml` lo monta ahora en solo lectura.
- **Verificado desde un clon limpio:**
  - sin Docker: `nvm install`, `make install`, `make check` (327 tests del backend y 93 de la web) y `make eval` (6/6 · 6/6);
  - con Docker: build sin caché, servicios *healthy*, la evaluación dentro del contenedor en 6/6 · 6/6, todas las URLs y los `curl` del README, y las cuatro preguntas de ejemplo con los ids esperados.
- Trello: T4 → «En curso».

---

## Paso 21 · Demo en línea en Vercel — 2026-11-26 (rama `deploy`)
- Con la entrega terminada, decidí añadir una demo en línea en Vercel, en una rama aparte para no tocar `main` hasta que funcionara. La IA estudió antes la documentación de Vercel y me propuso el `vercel.json`; elegí probarlo con la CLI de Vercel, con despliegues de vista previa.
- Tres intentos:
  1. Incluir `../datos` en la función: Vercel lo rechaza (no admite rutas con `..`).
  2. Copiar `datos/pois.json` dentro de la API al construir: el catálogo carga con sus 7 avisos, pero el prefijo `/api` no se quitaba con `routes`.
  3. Quitar el prefijo con una `rewrite` del servicio: funciona.
- Decisión D-052: Demo en línea en Vercel con Services, sin cambiar la app.
- Variable `RUTA_POIS=datos/pois.json` añadida al proyecto de Vercel (producción y vista previa). La CLI añadió `.vercel` al `.gitignore`.
- **Verificado en la vista previa:** la portada, el listado y la ficha al recargar; `/api/pois`, `/api/pois/poi-003`, `/api/docs` y `/openapi.json` (200); el duplicado poi-004 (404); un 422 en inglés, y las 6 preguntas de la evaluación con los mismos ids que en local.
- Al ser el primer despliegue del proyecto, la CLI lo lanzó como producción y conectó el repositorio de GitHub; ese intento falló y no publicó nada.
- Pendiente: comprobar la vista previa que sale del push a `deploy`, fusionar en `main`, verificar la URL de producción y añadirla al README.

---

## Paso 22 · `feat/ultimos-ajustes`: remitir a la Oficina de Turismo — 2026-11-26
- Fusioné `deploy` en `main` antes de abrir la rama, para que el siguiente push a `main` no desplegara producción sin `vercel.json`. Producción (https://valdelumbre-asistente.vercel.app) verificada: rutas, 404, 422 y `make eval EVAL_URL=https://valdelumbre-asistente.vercel.app/api` en 6/6 · 6/6.
- Ticket de última hora en Trello: **H13 · Que el asistente remita a la Oficina de Turismo cuando no sabe**.
- Elegí nombrarla en el texto sin citarla, y los casos en que remite. Decisión D-053, que revisa D-032.
- TDD: primero `tests/test_tourist_office.py` (buscarla por nombre, sin Oficina en el catálogo, horario en palabras en es/en, rangos de días, varias franjas, siempre abierta, horario desconocido o por temporadas) y casos nuevos en `test_empty_answer.py`, `test_template_generator.py` y `test_ask_endpoint.py`. Comprobé que fallaban (8 tests y el módulo nuevo).
- Ficheros nuevos: `app/assistant/tourist_office.py` (encontrarla y la frase de remisión) y `app/assistant/opening_hours_text.py` (el horario en palabras). Los nombres de los días y la unión con «y» pasan a `template_texts.py`, que ya comparten la respuesta vacía y el horario.
- Comprobado con el catálogo real: la tirolina (es/en), el wifi y los perros remiten con el horario; «¿Qué museos abren el lunes?» y «¿Es accesible el puente romano?» no remiten; «¿Dónde está la oficina de turismo?» sigue citando su ficha.
- Verificado: `make check` limpio (343 tests del backend y 93 de la web) y `make eval` en 6/6 · 6/6.

---

## Paso 23 · Que el asistente responda a todo lo que permiten los datos — 2026-11-26
- Probé el asistente con preguntas reales y encontré que «¿qué hay cerrado ahora mismo?» listaba los lugares abiertos. Pedí que respondiera a todas las preguntas que permiten los datos.
- La IA hizo una ronda de 34 preguntas, una o varias por cada campo del catálogo, y encontró **cinco respuestas contrarias a la pregunta** (cerrado, no accesible, «menos de 5 euros» → aparcamiento) y nueve preguntas razonables sin respuesta. La IA estimó 3–4 horas; le pedí hacerlo más rápido y lo terminó en menos de una, con test primero.
- Ticket de última hora: **H14 · Que el asistente responda a todo lo que permiten los datos**. Decisión D-054.
- TDD: primero `tests/test_ask_coverage.py` (27 casos con el catálogo real). Antes de fijar los valores esperados, la IA los contrastó con `GET /pois` y con el JSON: había escrito mal los horarios de los museos en el test, y lo corrigió con los datos reales.
- Ficheros nuevos en `app/assistant/interpretation/`, uno por señal: `closed.py`, `price.py`, `hours.py`, `sights.py` y `name_synonyms.py`. Cambios en `accessibility.py` (negaciones), `opening_time.py` (momentos del día y «mañana»), `poi_filter.py` (cerrado, accesibilidad desconocida, gratis y precio máximo), `retrieval.py` (qué ver y lo más barato), `template_generator.py` y `opening_hours_text.py` (horario en la respuesta, agrupando las franjas de los mismos días).
- Fallos propios corregidos antes de entregar:
  - el filtro de cerrado dejaba pasar los horarios desconocidos como abiertos (lo detectaron los tests de `GET /pois`);
  - «no cuesta nada» convirtió «cuesta» en vocabulario y rompió «Tell me about Cuesta Car Park»;
  - «Is there free wifi?» se leía como «gratis»;
  - el castillo repetía los días en sus dos franjas.
- Verificado: `make check` limpio (387 tests del backend y 93 de la web) y `make eval` en 6/6 · 6/6.

---

## Paso 24 · Cercanía y más formas de decir «gratis» — 2026-11-26
- Probando la pantalla vi que «¿qué puedo hacer sin dinero?» listaba también lugares de pago: solo se reconocían «sin gastar» y «sin pagar». En lugar de añadir frases sueltas, la IA lo cambió por una regla: «sin»/«without»/«no» seguido de una palabra de dinero («sin dinero», «sin gastar nada», «without spending money»). Con `tests/test_interpret_price.py`.
- **Cercanía** (D-054): «¿qué hay cerca del castillo?» da los 5 lugares más cercanos, ordenados y con su distancia en línea recta, y se combina con los filtros («restaurantes cerca de la plaza», «museums near the main square»).
  - TDD con el catálogo real. Antes de fijar las distancias esperadas, la IA las calculó con los datos: había puesto de memoria 1,0 y 1,6 km para dos museos, que en realidad están a 370 y 580 m.
  - `Coordinates.metres_to()` en el dominio, con la misma aproximación que el mapa de la web; `nearby()` en `retrieval.py` y `nearby_answer.py` para el texto.
  - «What is near the winery?»: «winery» es el tema «vino», que solo tiene un lugar, así que se mide desde la bodega. «¿Dónde como cerca de la iglesia?»: «dónde como» se entiende ahora como comer.
- Verificado: `make check` limpio (413 tests del backend y 93 de la web) y `make eval` en 6/6 · 6/6.

---

## Paso 25 · Esqueleto de carga para el arranque en frío de Vercel — 2026-11-26
- La IA me explicó a favor y en contra. Le propuse hacerlo solo en el despliegue; me recomendó un solo código que solo muestre el esqueleto si la carga tarda más de 300 ms, y lo aprobé. Decisión D-055. Tarjeta **T6**.
- TDD: primero `loading/delayed-loading.spec.ts` (reloj falso: a los 299 ms no, a los 300 sí, se apaga al terminar y nunca aparece si la carga dura menos) y un test por pantalla (listado, ficha y tarjetas citadas: aparece, está oculto al lector y desaparece al llegar los datos). Fallaban porque el módulo no existía.
- Ficheros nuevos en `web/src/app/loading/`: `delayed-loading.ts`, `skeleton-cards.ts` y `skeleton-detail.ts`.
- **Probado en Chrome con una API lenta de verdad:** un proxy temporal que retrasa cada respuesta 1,5 s, en puertos aparte.
  - El listado y la ficha muestran su esqueleto con «Cargando…» y lo quitan al llegar los datos (17 tarjetas).
  - En el asistente, el esqueleto aparece 300 ms después de la respuesta, con un hueco por lugar citado, y desaparece al llegar la tarjeta (medido con un `MutationObserver`).
  - Con la API local normal **no aparece nunca**.
- Verificado: `make check` limpio (413 tests del backend y 99 de la web).

---

## Paso 26 · Repaso final de la documentación y verificación — 2026-11-26
- **README:** enlace a la demo en línea, cómo evaluar contra ella (`EVAL_URL=…/api`), las preguntas nuevas en «Qué probar», las mejoras de los pasos 22–25 en «Qué incluye», Vercel en las tecnologías, las decisiones D-053 y D-054, las limitaciones actualizadas («car park» ya funciona) y «qué haría con más tiempo» sin lo ya hecho.
- **IA.md:** la remisión a la Oficina que rechacé y recuperé, el esqueleto solo en el despliegue que la IA desaconsejó, el bug de las negaciones, los valores de memoria corregidos con los datos, la CLI de Vercel y la estimación de 3–4 horas que se hizo en menos de una.
- Al comprobar los enlaces aparecieron **tres anclas rotas en el README** (D-029, D-033 y D-037), escritas sin comprobar el título exacto. Corregidas; ahora un script comprueba todas las anclas de los cuatro documentos: 0 rotas.
- **Verificado antes de fusionar:**
  - clon limpio de `feat/ultimos-ajustes` desde GitHub y `docker compose build --no-cache`: servicios *healthy*, la web, una ficha y `/docs` responden, la evaluación dentro del contenedor da 6/6 · 6/6, y las preguntas nuevas (cerrado, horario, sin dinero, cercanía, tirolina) responden bien;
  - la vista previa de Vercel de la rama: rutas, `/api/docs` y las mismas preguntas;
  - `make check` limpio (413 tests del backend y 99 de la web).

