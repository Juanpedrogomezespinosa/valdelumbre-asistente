---
paths:
  - "*.md"
  - "docs/**"
---

# Reglas · Documentación

- Destinatario: un evaluador que **no** tendrá una sesión con el autor. Todo debe entenderse leyéndolo.
- `README.md`: cómo arrancarlo (comandos copiables y **verificados**), decisiones resumidas y qué haría con más tiempo. Cuando un comando marcado ⏳ quede implementado y probado, se le quita la marca.
- `docs/DECISIONES.md`: formato fijo Contexto / Decisión / Por qué / Alternativas descartadas / Consecuencias. Una decisión que cambia no se borra: se marca 🔄 y se enlaza la nueva.
- `DATOS.md`: un apartado por defecto (qué, dónde, riesgo, qué se hizo y test que lo cubre).
- `IA.md`: qué se pidió, qué se aceptó y, sobre todo, **qué se corrigió o descartó y por qué**. Con ejemplos concretos.
- `docs/BITACORA.md`: cronológico, una entrada por paso, con fecha.
- Nada de afirmaciones no comprobadas ("funciona", "todos los tests pasan") sin haberlo ejecutado.
