from app.data.quality import DataWarning
from app.data.raw import RawPoi
from app.data.rules.price import normalize_price
from app.data.rules.schedule import normalize_schedule
from app.data.rules.text import normalize_text
from app.domain.coordinates import Coordinates
from app.domain.poi import Poi


def to_poi(raw: RawPoi, coordinates: Coordinates | None) -> tuple[Poi, list[DataWarning]]:
    name, name_warnings = normalize_text(raw.id, "nombre", es=raw.nombre.es, en=raw.nombre.en)
    description, description_warnings = normalize_text(
        raw.id, "descripcion", es=raw.descripcion.es, en=raw.descripcion.en
    )
    schedule, schedule_warnings = normalize_schedule(raw.id, raw.horario)
    price, price_warnings = normalize_price(raw.id, raw.precio)

    poi = Poi(
        id=raw.id,
        name=name,
        category=raw.categoria,
        description=description,
        coordinates=coordinates,
        accessible=raw.accesible,
        schedule=schedule,
        price=price,
        tags=tuple(raw.etiquetas),
    )
    warnings = [*name_warnings, *description_warnings, *schedule_warnings, *price_warnings]
    return poi, warnings
