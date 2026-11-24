from datetime import time

from app.data.quality import DataWarning, WarningKind
from app.data.raw import RawSchedule, RawSlot
from app.data.rules.schedule import normalize_schedule
from app.domain.schedule import Season, TimeSlot


def raw_slot(dias: list[int], abre: str, cierra: str, temporada: str | None = None) -> RawSlot:
    return RawSlot(dias=dias, abre=abre, cierra=cierra, temporada=temporada)


def kinds(warnings: list[DataWarning]) -> list[WarningKind]:
    return [warning.kind for warning in warnings]


def test_always_open_schedule_is_kept() -> None:
    schedule, warnings = normalize_schedule("poi-x", RawSchedule(always_open=True, franjas=[]))

    assert schedule.always_open
    assert warnings == []


def test_slots_become_domain_slots() -> None:
    raw = RawSchedule(always_open=False, franjas=[raw_slot([1, 2], "10:00", "14:00")])

    schedule, warnings = normalize_schedule("poi-x", raw)

    assert schedule.slots == (TimeSlot(frozenset({1, 2}), time(10, 0), time(14, 0)),)
    assert warnings == []


def test_season_text_becomes_a_season() -> None:
    raw = RawSchedule(
        always_open=False, franjas=[raw_slot([1], "11:00", "20:00", temporada="06-01/09-30")]
    )

    schedule, _ = normalize_schedule("poi-014", raw)

    assert schedule.slots[0].season == Season(start=(6, 1), end=(9, 30))


def test_schedule_without_slots_is_unknown_with_warning() -> None:
    schedule, warnings = normalize_schedule("poi-018", RawSchedule(always_open=False, franjas=[]))

    assert not schedule.is_known
    assert kinds(warnings) == [WarningKind.UNKNOWN_SCHEDULE]


def test_slot_crossing_midnight_is_dropped_with_warning() -> None:
    raw = RawSchedule(
        always_open=False,
        franjas=[raw_slot([5], "22:00", "02:00"), raw_slot([5], "10:00", "14:00")],
    )

    schedule, warnings = normalize_schedule("poi-x", raw)

    assert len(schedule.slots) == 1
    assert kinds(warnings) == [WarningKind.INVALID_SLOT]


def test_slot_with_unreadable_season_is_dropped_with_warning() -> None:
    raw = RawSchedule(
        always_open=False, franjas=[raw_slot([1], "10:00", "14:00", temporada="verano")]
    )

    schedule, warnings = normalize_schedule("poi-x", raw)

    assert kinds(warnings) == [WarningKind.INVALID_SLOT, WarningKind.UNKNOWN_SCHEDULE]
    assert not schedule.is_known
