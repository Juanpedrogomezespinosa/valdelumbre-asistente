from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from app.domain.opening_query import OpeningQuery
from app.routes.open_at_param import parse_open_at

MADRID = ZoneInfo("Europe/Madrid")
NOW = datetime(2026, 11, 23, 12, 0, tzinfo=MADRID)


def test_weekday_and_time_use_today_to_resolve_seasons() -> None:
    assert parse_open_at("3T09:30", NOW) == OpeningQuery(
        weekday=3, at=time(9, 30), reference_date=date(2026, 11, 23)
    )


def test_a_full_date_and_time_resolves_its_own_weekday_and_season() -> None:
    assert parse_open_at("2026-07-06T12:00", NOW) == OpeningQuery(
        weekday=1, at=time(12, 0), reference_date=date(2026, 7, 6)
    )


def test_a_date_and_time_with_offset_is_converted_to_village_time() -> None:
    # 23:30 UTC on a Sunday in July is already Monday 01:30 in Madrid (UTC+2).
    assert parse_open_at("2026-07-05T23:30:00+00:00", NOW) == OpeningQuery(
        weekday=1, at=time(1, 30), reference_date=date(2026, 7, 6)
    )


@pytest.mark.parametrize(
    "value",
    ["", "lunes", "0T12:00", "8T12:00", "1T25:00", "1T12", "1 12:00", "2026-07-06", "mañana"],
)
def test_rejects_anything_else(value: str) -> None:
    with pytest.raises(ValueError):
        parse_open_at(value, NOW)
