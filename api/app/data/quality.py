from dataclasses import dataclass
from enum import StrEnum


class WarningKind(StrEnum):
    UNPARSEABLE_PRICE = "unparseable_price"


@dataclass(frozen=True)
class DataWarning:
    poi_id: str
    kind: WarningKind
    detail: str
    action: str
