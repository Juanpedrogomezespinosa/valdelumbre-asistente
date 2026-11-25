from app.domain.localized_text import LocalizedText
from app.domain.poi import Category, Poi
from app.domain.price import Price
from app.domain.schedule import Schedule

ALWAYS_OPEN = Schedule(always_open=True, slots=())


def make_poi(
    poi_id: str,
    *,
    name: LocalizedText | None = None,
    category: Category = Category.MONUMENT,
    accessible: bool | None = None,
    schedule: Schedule = ALWAYS_OPEN,
    tags: tuple[str, ...] = (),
    description: str = "",
) -> Poi:
    return Poi(
        id=poi_id,
        name=name or LocalizedText(es=poi_id),
        category=category,
        description=LocalizedText(es=description),
        coordinates=None,
        accessible=accessible,
        schedule=schedule,
        price=Price.unknown(),
        tags=tags,
    )
