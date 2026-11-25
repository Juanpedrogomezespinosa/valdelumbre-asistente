from app.assistant.interpretation.phrases import contains_any


def _each(phrases: tuple[str, ...], subject: str) -> dict[str, str]:
    return dict.fromkeys(phrases, subject)


# Things visitors ask about that the assistant does not look up (D-050): without this, "is
# there wifi in the park?" listed the park as if the answer were yes.
UNRECORDED_PHRASES: dict[str, str] = {
    **_each(("wifi", "wi-fi", "wi fi", "internet"), "wifi"),
    **_each(
        ("perro", "perros", "gato", "gatos", "mascota", "mascotas", "dog", "dogs", "pet", "pets"),
        "mascotas",
    ),
    **_each(
        (
            "aseo",
            "aseos",
            "banos",
            "lavabo",
            "lavabos",
            "wc",
            "toilet",
            "toilets",
            "restroom",
            "restrooms",
            "bathroom",
            "bathrooms",
        ),
        "aseos",
    ),
    **_each(
        ("tarjeta", "tarjetas", "efectivo", "bizum", "card", "cards", "cash", "pay by"), "pago"
    ),
    **_each(
        ("reserva", "reservas", "reservar", "booking", "book", "reservation", "reservations"),
        "reservas",
    ),
    **_each(
        ("visita guiada", "visitas guiadas", "guiada", "guiadas", "guided", "guided tour"),
        "visitas_guiadas",
    ),
    **_each(("terraza", "terrazas", "terrace", "terraces"), "terraza"),
    **_each(("cajero", "cajeros", "atm", "cash machine"), "cajero"),
    **_each(
        (
            "vegano",
            "vegana",
            "veganos",
            "vegetariano",
            "vegetariana",
            "sin gluten",
            "celiaco",
            "celiacos",
            "vegan",
            "vegetarian",
            "gluten",
            "gluten free",
        ),
        "dietas",
    ),
}


def unrecorded_in(folded: str) -> frozenset[str]:
    return frozenset(
        subject for phrase, subject in UNRECORDED_PHRASES.items() if contains_any(folded, (phrase,))
    )
