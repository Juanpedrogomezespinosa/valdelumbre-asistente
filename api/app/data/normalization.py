import re
from decimal import Decimal

from app.data.quality import DataWarning, WarningKind
from app.domain.price import Price

RawPrice = float | int | str | None

_FREE_WORDS = frozenset({"gratis", "gratuito", "free"})
_AMOUNT = r"(\d+(?:[.,]\d+)?)"
_SINGLE_AMOUNT = re.compile(rf"{_AMOUNT}\s*€?")
_EN_DASH = "\u2013"
_AMOUNT_RANGE = re.compile(rf"{_AMOUNT}\s*[-{_EN_DASH}]\s*{_AMOUNT}\s*€?")


def normalize_price(poi_id: str, raw: RawPrice) -> tuple[Price, list[DataWarning]]:
    if raw is None:
        return Price.unknown(), []
    try:
        return _parse_price(raw), []
    except ValueError:
        warning = DataWarning(
            poi_id,
            WarningKind.UNPARSEABLE_PRICE,
            detail=f"Unparseable price: {raw!r}",
            action="Treated as unknown price",
        )
        return Price.unknown(), [warning]


def _parse_price(raw: float | int | str) -> Price:
    # bool is a subclass of int in Python, so it must be rejected explicitly.
    if isinstance(raw, bool):
        raise ValueError(f"Not a price: {raw!r}")
    if isinstance(raw, int | float):
        return Price.fixed(Decimal(str(raw)))

    text = raw.strip().casefold()
    if text in _FREE_WORDS:
        return Price.free()
    if match := _SINGLE_AMOUNT.fullmatch(text):
        return Price.fixed(_to_decimal(match[1]))
    if match := _AMOUNT_RANGE.fullmatch(text):
        return Price.between(_to_decimal(match[1]), _to_decimal(match[2]))
    raise ValueError(f"Unrecognised price text: {raw!r}")


def _to_decimal(amount: str) -> Decimal:
    return Decimal(amount.replace(",", "."))
