import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "evaluate.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("evaluate", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluate = load_script()


def case(includes: set[str], excludes: set[str]) -> object:
    return evaluate.Case(
        id="q",
        language="es",
        question="?",
        includes=frozenset(includes),
        excludes=frozenset(excludes),
    )


@pytest.mark.parametrize(
    ("cited", "official"),
    [
        ({"poi-003", "poi-015"}, True),
        ({"poi-003", "poi-015", "poi-001"}, True),
        ({"poi-003"}, False),
        ({"poi-003", "poi-015", "poi-013"}, False),
    ],
)
def test_official_criterion_needs_every_included_and_no_excluded_id(
    cited: set[str], official: bool
) -> None:
    result = evaluate.score(case({"poi-003", "poi-015"}, {"poi-013"}), tuple(sorted(cited)))

    assert result.official is official
    assert result.strict is official


def test_reports_missing_and_forbidden_ids() -> None:
    result = evaluate.score(case({"poi-003", "poi-015"}, {"poi-013"}), ("poi-003", "poi-013"))

    assert result.missing == frozenset({"poi-015"})
    assert result.forbidden == frozenset({"poi-013"})


def test_strict_criterion_cites_nothing_when_nothing_is_expected() -> None:
    nothing_expected = case(set(), set())

    assert evaluate.score(nothing_expected, ("poi-010",)).official is True
    assert evaluate.score(nothing_expected, ("poi-010",)).strict is False
    assert evaluate.score(nothing_expected, ()).strict is True


def test_strict_criterion_equals_official_when_something_is_excluded() -> None:
    only_exclusions = case(set(), {"poi-013"})

    assert evaluate.score(only_exclusions, ("poi-003",)).strict is True


def test_the_assistant_passes_the_whole_evaluation_in_process(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = evaluate.main([])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Oficial: 6/6" in output
    assert "Estricto: 6/6" in output


def test_a_failing_question_gives_a_non_zero_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    impossible = tmp_path / "evaluacion.json"
    impossible.write_text(
        '[{"id": "qx", "idioma": "es", "pregunta": "¿Hay tirolina?",'
        ' "esperado_incluye": ["poi-001"], "esperado_excluye": []}]',
        encoding="utf-8",
    )

    exit_code = evaluate.main(["--evaluacion", str(impossible)])

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "faltan: poi-001" in output
    assert "Oficial: 0/1" in output


def test_an_unreachable_server_is_explained_without_a_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def refuse(*args: object, **kwargs: object) -> None:
        raise evaluate.urllib.error.URLError("Connection refused")

    monkeypatch.setattr(evaluate.urllib.request, "urlopen", refuse)

    exit_code = evaluate.main(["--url", "http://localhost:8799"])

    assert exit_code == 2
    assert "No se pudo conectar con http://localhost:8799" in capsys.readouterr().err
