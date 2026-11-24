import os
from pathlib import Path

_DEFAULT_CATALOG = Path(__file__).resolve().parents[2] / "datos" / "pois.json"


def catalog_path() -> Path:
    return Path(os.environ.get("RUTA_POIS", _DEFAULT_CATALOG))
