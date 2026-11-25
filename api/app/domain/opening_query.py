from dataclasses import dataclass
from datetime import date, time

from app.domain.schedule import ISO_WEEKDAYS


@dataclass(frozen=True)
class OpeningQuery:
    """A moment to check opening hours at; `reference_date` only decides seasons (D-011)."""

    weekday: int
    at: time
    reference_date: date

    def __post_init__(self) -> None:
        if self.weekday not in ISO_WEEKDAYS:
            raise ValueError(f"Weekday must be an ISO weekday number 1-7: {self.weekday}")
