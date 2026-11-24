from decimal import Decimal

from app.domain.localized_text import Language
from app.domain.price import Price

_UNKNOWN = {Language.ES: "Sin datos", Language.EN: "No data"}
_FREE = {Language.ES: "Gratis", Language.EN: "Free"}
_EN_DASH = "\u2013"


def price_text(price: Price, language: Language) -> str:
    if price.min_eur is None or price.max_eur is None:
        return _UNKNOWN[language]
    if price.is_free:
        return _FREE[language]

    low = _amount(price.min_eur, language)
    high = _amount(price.max_eur, language)
    amount = low if low == high else f"{low}{_EN_DASH}{high}"
    return f"{amount} €" if language is Language.ES else f"€{amount}"


def _amount(value: Decimal, language: Language) -> str:
    text = f"{value:.0f}" if value == value.to_integral_value() else f"{value:.2f}"
    return text.replace(".", ",") if language is Language.ES else text
