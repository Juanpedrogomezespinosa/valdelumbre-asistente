from app.domain.localized_text import Language


def poi_not_found(poi_id: str, language: Language) -> str:
    if language is Language.EN:
        return f"There is no point of interest with id {poi_id}"
    return f"No existe ningún punto con id {poi_id}"
