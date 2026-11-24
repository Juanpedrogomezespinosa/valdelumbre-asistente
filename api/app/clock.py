from collections.abc import Callable
from datetime import datetime

from app.settings import village_time_zone

Clock = Callable[[], datetime]


def village_now() -> datetime:
    return datetime.now(village_time_zone())
