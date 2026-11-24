from dataclasses import dataclass
from enum import StrEnum


class WarningKind(StrEnum):
    UNPARSEABLE_PRICE = "unparseable_price"
    INJECTED_INSTRUCTION = "injected_instruction"
    MISSING_TRANSLATION = "missing_translation"
    SWAPPED_COORDINATES = "swapped_coordinates"
    OUTLIER_COORDINATES = "outlier_coordinates"
    DUPLICATE_POI = "duplicate_poi"
    INVALID_SLOT = "invalid_slot"
    UNKNOWN_SCHEDULE = "unknown_schedule"


@dataclass(frozen=True)
class DataWarning:
    poi_id: str
    kind: WarningKind
    detail: str
    action: str
