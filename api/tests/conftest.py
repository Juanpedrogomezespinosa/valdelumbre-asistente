from collections.abc import Iterator
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.dependencies import get_clock

A_NOVEMBER_MONDAY_AT_NOON = datetime(2026, 11, 23, 12, 0, tzinfo=ZoneInfo("Europe/Madrid"))


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_clock] = lambda: lambda: A_NOVEMBER_MONDAY_AT_NOON
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
