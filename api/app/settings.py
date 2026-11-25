import os
from pathlib import Path
from zoneinfo import ZoneInfo

_DEFAULT_CATALOG = Path(__file__).resolve().parents[2] / "datos" / "pois.json"


def catalog_path() -> Path:
    return Path(os.environ.get("RUTA_POIS", _DEFAULT_CATALOG))


def village_time_zone() -> ZoneInfo:
    return ZoneInfo(os.environ.get("ZONA_HORARIA", "Europe/Madrid"))
