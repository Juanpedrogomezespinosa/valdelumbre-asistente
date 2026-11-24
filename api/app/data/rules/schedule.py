import re

from app.data.quality import DataWarning, WarningKind
from app.data.raw import RawSchedule, RawSlot
from app.domain.schedule import Schedule, Season, TimeSlot

_SEASON = re.compile(r"(\d{2})-(\d{2})/(\d{2})-(\d{2})")


def normalize_schedule(poi_id: str, raw: RawSchedule) -> tuple[Schedule, list[DataWarning]]:
    slots: list[TimeSlot] = []
    warnings: list[DataWarning] = []
    for raw_slot in raw.franjas:
        try:
            slots.append(_to_slot(raw_slot))
        except ValueError as error:
            warnings.append(
                DataWarning(
                    poi_id,
                    WarningKind.INVALID_SLOT,
                    detail=f"Invalid opening slot: {error}",
                    action="Slot discarded",
                )
            )

    schedule = Schedule(always_open=raw.always_open, slots=tuple(slots))
    if not schedule.is_known:
        warnings.append(
            DataWarning(
                poi_id,
                WarningKind.UNKNOWN_SCHEDULE,
                detail="Not always open and without opening slots",
                action="Opening hours served as unknown, never as closed",
            )
        )
    return schedule, warnings


def _to_slot(raw: RawSlot) -> TimeSlot:
    season = None if raw.temporada is None else _parse_season(raw.temporada)
    return TimeSlot(frozenset(raw.dias), raw.abre, raw.cierra, season)


def _parse_season(text: str) -> Season:
    match = _SEASON.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"Unreadable season: {text!r}")
    start_month, start_day, end_month, end_day = map(int, match.groups())
    return Season(start=(start_month, start_day), end=(end_month, end_day))
