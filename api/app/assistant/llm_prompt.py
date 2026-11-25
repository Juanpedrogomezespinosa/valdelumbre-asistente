import json
from collections.abc import Sequence

from app.assistant import template_texts as texts
from app.assistant.interpretation.interpretation import Interpretation
from app.domain.localized_text import Language
from app.domain.poi import Poi

_LANGUAGE_NAME = {Language.ES: "español", Language.EN: "English"}

_SYSTEM = """Eres el asistente turístico de Valdelumbre, un pueblo pequeño. El pueblo se llama
exactamente Valdelumbre: no uses ningún otro nombre para él.
Escribe solo la introducción de la respuesta: una o dos frases breves y cercanas que contesten
a la pregunta del visitante. Después la aplicación añadirá la lista de lugares, así que no la
escribas, no enumeres los lugares y no copies sus ids.
Usa solo los datos del mensaje: no añadas lugares, horarios, precios ni ningún otro dato.
Puedes decir cuántos lugares hay ("numero_de_lugares").
Escribe en {language}."""

# One required field and nothing else: the reply is checked against this shape.
REPLY_SCHEMA = {
    "type": "object",
    "properties": {"introduccion": {"type": "string"}},
    "required": ["introduccion"],
    "additionalProperties": False,
}


def system_prompt(language: Language) -> str:
    return _SYSTEM.format(language=_LANGUAGE_NAME[language])


def user_message(interpretation: Interpretation, pois: Sequence[Poi], language: Language) -> str:
    """The question plus the same structured facts the template uses, never descriptions (D-043)."""
    return json.dumps(
        {
            "pregunta": interpretation.question,
            "numero_de_lugares": len(pois),
            "lugares": [_facts(poi, language) for poi in pois],
        },
        ensure_ascii=False,
    )


def _facts(poi: Poi, language: Language) -> dict[str, object]:
    seasons = dict.fromkeys(slot.season for slot in poi.schedule.slots if slot.season)
    return {
        "id": poi.id,
        "nombre": poi.name.resolve(language).text,
        "categoria": texts.category(poi.category, language),
        "accesibilidad": texts.accessibility(poi.accessible, language),
        "temporadas": [texts.season(season, language) for season in seasons],
        "etiquetas": list(poi.tags),
    }
