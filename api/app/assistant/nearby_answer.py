from collections.abc import Sequence

from app.assistant.answer import Answer
from app.assistant.template_generator import place_line
from app.domain.localized_text import Language
from app.domain.poi import Poi

_KILOMETRE = 1000


def nearby_answer(
    anchor: Poi, closest: Sequence[tuple[Poi, float]], with_hours: bool, language: Language
) -> Answer:
    """The closest places to `anchor`, nearest first, with their straight-line distance."""
    name = anchor.name.resolve(language).text
    if language is Language.EN:
        introduction = f"Closest to {name}, in a straight line:"
    else:
        introduction = f"Lo más cercano a {name}, en línea recta:"
    lines = [
        f"{place_line(poi, language, with_hours)} · {_distance(metres, language)}"
        for poi, metres in closest
    ]
    return Answer(
        text="\n".join([introduction, *lines]),
        poi_ids=(anchor.id, *(poi.id for poi, _ in closest)),
    )


def _distance(metres: float, language: Language) -> str:
    # Rounded like the web's location text (web/src/app/pois/relative-location.ts).
    if metres < _KILOMETRE:
        amount = f"{round(metres / 10) * 10} m"
    else:
        amount = f"{metres / _KILOMETRE:.1f} km"
        amount = amount.replace(".", ",") if language is Language.ES else amount
    return f"{amount} away" if language is Language.EN else f"a {amount}"
