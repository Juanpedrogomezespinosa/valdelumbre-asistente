"""Run datos/evaluacion.json against POST /preguntar and report how many questions pass (D-016).

    cd api && uv run python ../scripts/evaluate.py                         # in process, no server
    cd api && uv run python ../scripts/evaluate.py --url http://localhost:8000

Exit code 1 if any question fails and 2 if the server cannot be reached, so it can run in CI.
"""

import argparse
import json
import logging
import sys
import urllib.error
import urllib.request
import warnings
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPOSITORY = Path(__file__).resolve().parents[1]
EVALUATION_FILE = REPOSITORY / "datos" / "evaluacion.json"

Ask = Callable[[str, str], tuple[str, ...]]


@dataclass(frozen=True)
class Case:
    id: str
    language: str
    question: str
    includes: frozenset[str]
    excludes: frozenset[str]


@dataclass(frozen=True)
class Result:
    case: Case
    cited: tuple[str, ...]
    missing: frozenset[str]
    forbidden: frozenset[str]
    official: bool
    strict: bool


def score(case: Case, cited: tuple[str, ...]) -> Result:
    missing = case.includes - set(cited)
    forbidden = case.excludes & set(cited)
    official = not missing and not forbidden
    # Own stricter criterion (D-016): with nothing expected, nothing may be cited.
    expects_nothing = not case.includes and not case.excludes
    strict = official and not (expects_nothing and cited)
    return Result(case, cited, frozenset(missing), frozenset(forbidden), official, strict)


def load_cases(path: Path) -> list[Case]:
    return [
        Case(
            id=raw["id"],
            language=raw["idioma"],
            question=raw["pregunta"],
            includes=frozenset(raw["esperado_incluye"]),
            excludes=frozenset(raw["esperado_excluye"]),
        )
        for raw in json.loads(path.read_text(encoding="utf-8"))
    ]


@contextmanager
def asking_in_process() -> Iterator[Ask]:
    # The script lives outside the api package; make `app` importable when run directly.
    sys.path.insert(0, str(REPOSITORY / "api"))
    # Keep the report readable: the server already logs the data warnings at startup,
    # and the httpx deprecation in the test client is known (BITACORA, step 8.1).
    warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient`")
    from fastapi.testclient import TestClient

    from app.main import app

    logging.disable(logging.CRITICAL)
    try:
        with TestClient(app) as client:

            def ask(question: str, language: str) -> tuple[str, ...]:
                body = {"pregunta": question, "idioma": language}
                return _cited_ids(client.post("/preguntar", json=body).json())

            yield ask
    finally:
        logging.disable(logging.NOTSET)


@contextmanager
def asking_over_http(url: str) -> Iterator[Ask]:
    def ask(question: str, language: str) -> tuple[str, ...]:
        request = urllib.request.Request(
            f"{url.rstrip('/')}/preguntar",
            data=json.dumps({"pregunta": question, "idioma": language}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return _cited_ids(json.load(response))

    yield ask


def _cited_ids(body: Any) -> tuple[str, ...]:
    return tuple(body["ids"])


def report(results: list[Result]) -> str:
    lines = [_result_line(result) for result in results]
    total = len(results)
    official = sum(result.official for result in results)
    strict = sum(result.strict for result in results)
    lines.append(f"\nOficial: {official}/{total} · Estricto: {strict}/{total}")
    return "\n".join(lines)


def _result_line(result: Result) -> str:
    official = "✔" if result.official else "✘"
    strict = "✔" if result.strict else "✘"
    cited = ", ".join(result.cited) or "ninguno"
    line = f"{result.case.id}  oficial {official}  estricto {strict}  citados: {cited}"
    if result.missing:
        line += f"  · faltan: {', '.join(sorted(result.missing))}"
    if result.forbidden:
        line += f"  · prohibidos: {', '.join(sorted(result.forbidden))}"
    if result.official and not result.strict:
        line += "  · no debía citar nada"
    return line


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evalúa el asistente con datos/evaluacion.json (D-016)."
    )
    parser.add_argument("--url", help="servidor de la API; sin él, se evalúa en proceso")
    parser.add_argument(
        "--evaluacion", type=Path, default=EVALUATION_FILE, help="fichero de preguntas a evaluar"
    )
    arguments = parser.parse_args(argv)

    cases = load_cases(arguments.evaluacion)
    asking = asking_over_http(arguments.url) if arguments.url else asking_in_process()
    try:
        with asking as ask:
            results = [score(case, ask(case.question, case.language)) for case in cases]
    except urllib.error.URLError as error:
        print(
            f"No se pudo conectar con {arguments.url}: {error.reason}. "
            "¿Está la API en marcha (make api)?",
            file=sys.stderr,
        )
        return 2

    print(report(results))
    return 0 if all(result.strict for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
