from datetime import date, time

import pytest

from app.domain.schedule import Schedule, Season, TimeSlot

MONDAY, TUESDAY, SATURDAY = 1, 2, 6
A_NOVEMBER_DAY = date(2026, 11, 23)
A_JULY_DAY = date(2026, 7, 6)

WEEKDAYS_EXCEPT_SUNDAY = frozenset(range(1, 7))
WEEKDAYS_EXCEPT_MONDAY = frozenset(range(2, 8))
EVERY_DAY = frozenset(range(1, 8))
SUMMER = Season(start=(6, 1), end=(9, 30))


def slot(
    weekdays: frozenset[int], opens: str, closes: str, season: Season | None = None
) -> TimeSlot:
    return TimeSlot(weekdays, time.fromisoformat(opens), time.fromisoformat(closes), season)


def schedule(*slots: TimeSlot) -> Schedule:
    return Schedule(always_open=False, slots=slots)


def test_always_open_is_open_at_any_moment() -> None:
    always = Schedule(always_open=True, slots=())

    assert always.is_open(SATURDAY, time(3, 0), A_NOVEMBER_DAY) is True


def test_schedule_without_slots_is_unknown_not_closed() -> None:
    unknown = schedule()

    assert unknown.is_open(MONDAY, time(12, 0), A_NOVEMBER_DAY) is None


def test_weekday_one_is_monday_as_evaluation_q3_implies() -> None:
    castle = schedule(slot(WEEKDAYS_EXCEPT_SUNDAY, "10:00", "14:00"))
    olive_oil_museum = schedule(slot(WEEKDAYS_EXCEPT_MONDAY, "10:00", "18:00"))

    assert castle.is_open(MONDAY, time(12, 0), A_NOVEMBER_DAY) is True
    assert olive_oil_museum.is_open(MONDAY, time(12, 0), A_NOVEMBER_DAY) is False


@pytest.mark.parametrize(
    ("at", "expected"),
    [("11:00", True), ("15:00", False), ("18:00", True), ("21:00", False)],
)
def test_split_schedule_is_open_only_inside_its_slots(at: str, expected: bool) -> None:
    castle = schedule(
        slot(WEEKDAYS_EXCEPT_SUNDAY, "10:00", "14:00"),
        slot(WEEKDAYS_EXCEPT_SUNDAY, "17:00", "20:00"),
    )

    assert castle.is_open(TUESDAY, time.fromisoformat(at), A_NOVEMBER_DAY) is expected


@pytest.mark.parametrize(
    ("at", "expected"),
    [("09:59", False), ("10:00", True), ("13:59", True), ("14:00", False)],
)
def test_opening_time_is_inclusive_and_closing_time_exclusive(at: str, expected: bool) -> None:
    morning = schedule(slot(EVERY_DAY, "10:00", "14:00"))

    assert morning.is_open(MONDAY, time.fromisoformat(at), A_NOVEMBER_DAY) is expected


def test_seasonal_slot_only_applies_inside_its_season() -> None:
    natural_pool = schedule(slot(EVERY_DAY, "11:00", "20:00", season=SUMMER))

    assert natural_pool.is_open(MONDAY, time(12, 0), A_JULY_DAY) is True
    assert natural_pool.is_open(MONDAY, time(12, 0), A_NOVEMBER_DAY) is False


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        (date(2026, 5, 31), False),
        (date(2026, 6, 1), True),
        (date(2026, 9, 30), True),
        (date(2026, 10, 1), False),
    ],
)
def test_season_bounds_are_inclusive(day: date, expected: bool) -> None:
    assert SUMMER.includes(day) is expected


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        (date(2026, 11, 1), True),
        (date(2027, 1, 15), True),
        (date(2027, 2, 28), True),
        (date(2027, 3, 1), False),
        (date(2026, 7, 1), False),
    ],
)
def test_season_can_wrap_around_the_new_year(day: date, expected: bool) -> None:
    winter = Season(start=(11, 1), end=(2, 28))

    assert winter.includes(day) is expected


def test_slot_must_close_after_it_opens() -> None:
    with pytest.raises(ValueError, match="close after"):
        slot(EVERY_DAY, "22:00", "02:00")


@pytest.mark.parametrize("weekday", [0, 8])
def test_slot_weekdays_must_be_iso(weekday: int) -> None:
    with pytest.raises(ValueError, match="ISO weekday"):
        slot(frozenset({weekday}), "10:00", "14:00")


def test_season_must_use_real_calendar_days() -> None:
    with pytest.raises(ValueError):
        Season(start=(2, 30), end=(3, 1))


def test_schedule_is_known_when_always_open_or_with_slots() -> None:
    assert Schedule(always_open=True, slots=()).is_known
    assert schedule(slot(EVERY_DAY, "10:00", "14:00")).is_known
    assert not schedule().is_known
