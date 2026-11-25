import os
from pathlib import Path
from zoneinfo import ZoneInfo

_DEFAULT_CATALOG = Path(__file__).resolve().parents[2] / "datos" / "pois.json"


def catalog_path() -> Path:
    return Path(os.environ.get("RUTA_POIS", _DEFAULT_CATALOG))


def village_time_zone() -> ZoneInfo:
    return ZoneInfo(os.environ.get("ZONA_HORARIA", "Europe/Madrid"))


def answer_generator_name() -> str:
    """`plantilla` (default, no network) or `llm` (D-004, D-048)."""
    return os.environ.get("GENERADOR", "plantilla").strip().lower()


def llm_model() -> str:
    return os.environ.get("LLM_MODELO", "qwen2.5:3b")


def ollama_url() -> str:
    return os.environ.get("OLLAMA_URL", "http://localhost:11434")
