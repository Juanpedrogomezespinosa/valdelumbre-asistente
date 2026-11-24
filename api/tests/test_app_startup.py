import json
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_startup_loads_the_catalog_and_logs_its_data_warnings(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="valdelumbre")

    with TestClient(app):
        catalog = app.state.catalog

    assert len(catalog.pois) == 17
    assert "17 POIs, 7 data warnings" in caplog.text
    assert "poi-011 swapped_coordinates" in caplog.text
    assert "poi-013 injected_instruction" in caplog.text


def test_catalog_path_can_be_configured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    real_catalog = Path(__file__).resolve().parents[2] / "datos" / "pois.json"
    first_poi = json.loads(real_catalog.read_text(encoding="utf-8"))[:1]
    custom_catalog = tmp_path / "pois.json"
    custom_catalog.write_text(json.dumps(first_poi), encoding="utf-8")
    monkeypatch.setenv("RUTA_POIS", str(custom_catalog))

    with TestClient(app):
        assert [poi.id for poi in app.state.catalog.pois] == ["poi-001"]
