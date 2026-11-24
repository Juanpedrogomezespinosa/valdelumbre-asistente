---
name: registrar-decision
description: Registra una decisión de diseño o técnica en docs/DECISIONES.md y su paso en docs/BITACORA.md. Usar siempre que se apruebe, cambie o descarte una decisión del proyecto.
---

# Registrar una decisión

1. Lee `docs/DECISIONES.md` y localiza el último id (`D-0NN`). El nuevo es el siguiente.
2. Si la decisión **sustituye** a otra: no borres la antigua; cambia su estado a `🔄 revisada → D-0XX` y explica en la nueva qué cambió y por qué.
3. Añade la entrada al final con este formato exacto:

   ```markdown
   ## D-0NN · <título corto en forma de afirmación>
   **Estado:** ✅ aprobada · <AAAA-MM-DD>

   - **Contexto:** <qué problema o duda había; con datos concretos si los hay>
   - **Decisión:** <qué se hace>
   - **Por qué:** <razonamiento; preferir hechos verificables a opiniones>
   - **Alternativas descartadas:** <opción → motivo>
   - **Consecuencias:** <qué implica, incluidos sus costes>
   ```

4. Añade la fila al **índice** del principio (el ancla en GitHub es el título en minúsculas, con los espacios convertidos en guiones y sin signos de puntuación).
5. Añade una línea en `docs/BITACORA.md`, dentro del paso en curso: `- Decisión D-0NN: <título>`.
6. Si afecta a cómo se arranca o se usa el proyecto, actualiza también `README.md`.
7. No registres una decisión como aprobada si el usuario no la ha aprobado: en ese caso, déjala en la lista de "decisiones pendientes" de la bitácora.
