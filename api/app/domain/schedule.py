from dataclasses import dataclass
from datetime import date, time

ISO_WEEKDAYS = range(1, 8)
MonthDay = tuple[int, int]

# Any leap year works: it only validates month/day pairs, including 02-29.
_LEAP_YEAR = 2000


@dataclass(frozen=True)
class Season:
    start: MonthDay
    end: MonthDay

    def __post_init__(self) -> None:
        for month, day in (self.start, self.end):
            date(_LEAP_YEAR, month, day)

    def includes(self, day: date) -> bool:
        month_day = (day.month, day.day)
        if self.start <= self.end:
            return self.start <= month_day <= self.end
        # Wraps around the new year, e.g. from November to February.
        return month_day >= self.start or month_day <= self.end


@dataclass(frozen=True)
class TimeSlot:
    weekdays: frozenset[int]
    opens: time
    closes: time
    season: Season | None = None

    def __post_init__(self) -> None:
        if not self.weekdays or not self.weekdays <= set(ISO_WEEKDAYS):
            raise ValueError(f"Weekdays must be ISO weekday numbers 1-7: {sorted(self.weekdays)}")
        if self.closes <= self.opens:
            raise ValueError(f"A slot must close after it opens: {self.opens}-{self.closes}")

    def covers(self, weekday: int, at: time, reference_date: date) -> bool:
        in_season = self.season is None or self.season.includes(reference_date)
        return in_season and weekday in self.weekdays and self.opens <= at < self.closes


@dataclass(frozen=True)
class Schedule:
    always_open: bool
    slots: tuple[TimeSlot, ...]

    def is_open(self, weekday: int, at: time, reference_date: date) -> bool | None:
        """Return None when the opening hours are unknown: unknown is not closed (D-009).

        `reference_date` only decides whether seasonal slots apply, so a query by
        weekday alone can be answered against today's date (D-011).
        """
        if self.always_open:
            return True
        if not self.slots:
            return None
        return any(slot.covers(weekday, at, reference_date) for slot in self.slots)
