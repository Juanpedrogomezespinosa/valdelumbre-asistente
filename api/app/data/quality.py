from dataclasses import dataclass
from enum import StrEnum


class WarningKind(StrEnum):
    UNPARSEABLE_PRICE = "unparseable_price"
    INJECTED_INSTRUCTION = "injected_instruction"
    MISSING_TRANSLATION = "missing_translation"


@dataclass(frozen=True)
class DataWarning:
    poi_id: str
    kind: WarningKind
    detail: str
    action: str
