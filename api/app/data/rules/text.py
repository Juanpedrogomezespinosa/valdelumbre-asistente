import re

from app.data.quality import DataWarning, WarningKind
from app.domain.localized_text import LocalizedText
from app.domain.text_folding import fold

_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")
# Matched against lowercase, accent-free text. The defence does not rely on these
# patterns alone: facts are always read from structured fields (D-005, D-006).
_INJECTION_PATTERNS = (
    re.compile(r"\b(?:ignor|disregard|olvid|forget)\w*(?:\s+\w+){0,3}\s+(?:instruc|regla|rule)"),
    re.compile(r"\b(?:para|for)\s+(?:el|la|the)\s+(?:asistente|assistant|ia|ai|modelo|model)\b"),
    re.compile(r"\b(?:system prompt|prompt del sistema)\b"),
)


def normalize_text(
    poi_id: str, field: str, *, es: str, en: str | None
) -> tuple[LocalizedText, list[DataWarning]]:
    clean_es, warnings = _remove_injected_instructions(poi_id, field, es)
    clean_en, en_warnings = _remove_injected_instructions(poi_id, field, en or "")
    warnings += en_warnings
    if not clean_en:
        warnings.append(
            DataWarning(
                poi_id,
                WarningKind.MISSING_TRANSLATION,
                detail=f"No English text for {field}",
                action="Spanish text is served as fallback",
            )
        )
    return LocalizedText(es=clean_es, en=clean_en or None), warnings


def _remove_injected_instructions(
    poi_id: str, field: str, text: str
) -> tuple[str, list[DataWarning]]:
    sentences = _SENTENCE_BREAK.split(text.strip())
    injected = [sentence for sentence in sentences if _is_injected_instruction(sentence)]
    if not injected:
        return text.strip(), []

    kept = [sentence for sentence in sentences if sentence not in injected]
    warnings = [
        DataWarning(
            poi_id,
            WarningKind.INJECTED_INSTRUCTION,
            detail=f"Instruction aimed at the assistant in {field}: {sentence!r}",
            action="Sentence removed",
        )
        for sentence in injected
    ]
    return " ".join(kept), warnings


def _is_injected_instruction(sentence: str) -> bool:
    folded = fold(sentence)
    return any(pattern.search(folded) for pattern in _INJECTION_PATTERNS)
