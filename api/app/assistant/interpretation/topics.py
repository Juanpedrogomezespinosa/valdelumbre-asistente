from app.assistant.interpretation.phrases import contains_any


def _each(phrases: tuple[str, ...], topic: str) -> dict[str, str]:
    return dict.fromkeys(phrases, topic)


# Topics are catalog tags or category codes (folded). Accessibility is deliberately
# absent: it is decided by the structured field only (D-005).
TOPIC_PHRASES: dict[str, str] = {
    **_each(
        (
            "familia",
            "familias",
            "nino",
            "ninos",
            "nina",
            "ninas",
            "infantil",
            "hijos",
            "kids",
            "children",
            "child",
            "family",
            "families",
        ),
        "familias",
    ),
    **_each(
        ("vino", "vinos", "bodega", "bodegas", "cata", "wine", "wines", "winery", "tasting"),
        "vino",
    ),
    **_each(
        ("historia", "historico", "historica", "history", "historic", "historical"), "historia"
    ),
    **_each(("vistas", "mirador", "miradores", "view", "views", "viewpoint"), "vistas"),
    **_each(("atardecer", "puesta de sol", "sunset"), "atardecer"),
    **_each(("gastronomia", "gastronomy"), "gastronomia"),
    **_each(("compras", "tiendas", "mercado", "shopping", "shops", "market"), "compras"),
    **_each(("arte", "art"), "arte"),
    **_each(("naturaleza", "nature"), "naturaleza"),
    **_each(("senderismo", "caminar", "andar", "hiking", "hike", "walk", "walking"), "senderismo"),
    **_each(("verano", "banar", "banarse", "bano", "summer", "swim", "swimming"), "verano"),
}


def topics_in(folded: str) -> frozenset[str]:
    return frozenset(
        topic for phrase, topic in TOPIC_PHRASES.items() if contains_any(folded, (phrase,))
    )
