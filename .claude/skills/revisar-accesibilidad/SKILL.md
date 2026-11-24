---
name: revisar-accesibilidad
description: Checklist de accesibilidad (teclado y lector de pantalla) para revisar componentes Angular de web/ antes de darlos por terminados.
---

# Revisar la accesibilidad de la pantalla

Recorre cada componente modificado y comprueba:

## Estructura
- [ ] Un único `<h1>` y una jerarquía de encabezados sin saltos.
- [ ] Landmarks: `<header>`, `<main>`, `<nav>` si procede; enlace "Saltar al contenido".
- [ ] `<html lang>` correcto y `lang` en los fragmentos en otro idioma (fallback de traducción).

## Formularios
- [ ] Cada control tiene un `<label>` asociado (o `aria-label` si no hay texto visible).
- [ ] Los grupos (filtros) en `<fieldset>` + `<legend>`.
- [ ] Errores asociados con `aria-describedby` y anunciados.

## Teclado
- [ ] Se puede llegar a todo con Tab, en un orden lógico; nada atrapa el foco.
- [ ] El foco es visible (`:focus-visible`) con contraste suficiente.
- [ ] Botones de verdad (`<button>`), no `div` con `(click)`.
- [ ] Puntos del mapa SVG: enfocables, con nombre accesible y activables con Enter.

## Lector de pantalla
- [ ] La respuesta del asistente se anuncia en `aria-live="polite"`, y también el estado "Buscando…".
- [ ] El número de resultados se anuncia al filtrar.
- [ ] Las fichas son una lista (`<ul>`/`<li>`) con un encabezado por ficha.
- [ ] Los iconos decorativos llevan `aria-hidden="true"`; la información no depende solo del color o del icono.

## Visual
- [ ] Contraste AA (4.5:1 para texto normal).
- [ ] Usable con zoom al 200 % y a 320 px de ancho sin scroll horizontal.
- [ ] `prefers-reduced-motion` respetado.

## Verificación manual
- Navegar la pantalla completa solo con teclado.
- Pasar VoiceOver (macOS: `Cmd + F5`) por el flujo "preguntar → escuchar la respuesta → ir a una ficha".

Anota los hallazgos y su arreglo en `docs/BITACORA.md`.
