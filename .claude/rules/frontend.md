---
paths:
  - "web/**"
---

# Reglas · Frontend (Angular)

- Angular en su última versión estable: componentes **standalone**, **signals**, control de flujo nativo (`@if`, `@for`) y `inject()`.
- Debe pasar `npm run lint` (angular-eslint) y respetar el formato de Prettier.
- Rutas: `/`, `/pois` (filtros en la URL) y `/pois/:id`. Al navegar, mover el foco al `<h1>` y actualizar el `<title>` (D-027).
- Textos de la interfaz solo a través del servicio de idioma (D-028); nunca cadenas fijas en las plantillas.
- Tests con el runner del CLI y Angular Testing Library; buscar los elementos por rol y etiqueta, no por clase CSS (D-029).

## Estilos (Tailwind v4, D-026)
1. Solo los **tokens propios** definidos en `@theme` (colores con contraste AA comprobado); nada de colores arbitrarios (`bg-[#abc]`).
2. Un patrón que se repite → **componente Angular**, no `@apply`.
3. **Foco visible común** para toda la app; no quitar nunca el `outline` sin sustituirlo.
4. Aspecto de guía editorial cálida (terracota y oliva), con títulos en Fraunces y texto en Source Sans 3, servidas desde la app y nunca desde un CDN, y modo oscuro según el sistema, con un botón para elegir que recuerda la elección. Contraste AA comprobado **en los dos temas** (D-030, D-044, D-045).

## Componentes
- Una única tarjeta `<app-poi-card>` para el listado y el asistente: nombre, categoría, accesibilidad, «abierto ahora» y precio, con enlace a `/pois/:id` (D-031).
- Mapa SVG en `/pois`, solo al final y si da tiempo; complementario al listado (D-019).
- Las llamadas HTTP van a `/api/...` (proxy en desarrollo, nginx en Docker). Nunca URLs absolutas a `localhost`.
- Un servicio por recurso (`PoisService`, `AssistantService`); los componentes no usan `HttpClient` directamente.

## Accesibilidad (requisito del enunciado, no opcional)
- HTML semántico primero (`<main>`, `<nav>`, `<form>`, `<label>`, `<button>`, `<ul>`), ARIA solo cuando el HTML no baste.
- Todo usable **solo con teclado**: orden de tabulación lógico, foco siempre visible, nada que dependa de pasar el ratón.
- La respuesta del asistente se anuncia en una región `aria-live="polite"`; el estado de carga y los errores también.
- Al cambiar los filtros, anunciar el número de resultados ("7 puntos encontrados").
- Estados desconocidos en **texto** ("Sin datos de accesibilidad", "Horario no disponible"), nunca solo con color o icono.
- Texto en un idioma distinto al de la página → atributo `lang` en ese elemento.
- Contraste AA como mínimo; respetar `prefers-reduced-motion`.
- Tras cambios de interfaz, aplicar la skill `revisar-accesibilidad`.
