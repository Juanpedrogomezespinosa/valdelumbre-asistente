from datetime import datetime

from app.domain.localized_text import Language, LocalizedText
from app.domain.poi import Poi
from app.domain.price_text import price_text
from app.domain.schedule import Schedule, Season, TimeSlot
from app.routes.schemas import (
    CoordinatesResponse,
    PoiResponse,
    PriceResponse,
    ScheduleResponse,
    SeasonResponse,
    SlotResponse,
    TextResponse,
)


def present_poi(poi: Poi, language: Language, now: datetime) -> PoiResponse:
    coordinates = poi.coordinates
    return PoiResponse(
        id=poi.id,
        nombre=_text(poi.name, language),
        descripcion=_text(poi.description, language),
        categoria=poi.category,
        coordenadas=None
        if coordinates is None
        else CoordinatesResponse(lat=coordinates.lat, lon=coordinates.lon),
        accesible=poi.accessible,
        abierto_ahora=poi.schedule.is_open(now.isoweekday(), now.time(), now.date()),
        horario=_schedule(poi.schedule),
        precio=PriceResponse(
            minimo=None if poi.price.min_eur is None else float(poi.price.min_eur),
            maximo=None if poi.price.max_eur is None else float(poi.price.max_eur),
            texto=price_text(poi.price, language),
        ),
        etiquetas=list(poi.tags),
    )


def _text(text: LocalizedText, language: Language) -> TextResponse:
    resolved = text.resolve(language)
    served_language = Language.ES if resolved.is_fallback else language
    return TextResponse(texto=resolved.text, idioma=served_language)


def _schedule(schedule: Schedule) -> ScheduleResponse:
    return ScheduleResponse(
        siempre_abierto=schedule.always_open,
        conocido=schedule.is_known,
        franjas=[_slot(slot) for slot in schedule.slots],
    )


def _slot(slot: TimeSlot) -> SlotResponse:
    return SlotResponse(
        dias=sorted(slot.weekdays),
        abre=slot.opens.strftime("%H:%M"),
        cierra=slot.closes.strftime("%H:%M"),
        temporada=None if slot.season is None else _season(slot.season),
    )


def _season(season: Season) -> SeasonResponse:
    return SeasonResponse(desde=_month_day(season.start), hasta=_month_day(season.end))


def _month_day(month_day: tuple[int, int]) -> str:
    month, day = month_day
    return f"{month:02d}-{day:02d}"
