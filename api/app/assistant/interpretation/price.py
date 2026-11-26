import re
from decimal import Decimal

from app.assistant.interpretation.phrases import contains_any

FREE_PHRASES = (
    "gratis",
    "gratuito",
    "gratuitos",
    "gratuita",
    "gratuitas",
    "sin gastar",
    "sin pagar",
    "no cuesta nada",
    "no cuestan nada",
    "free",
    "for free",
    "no cost",
)
CHEAPEST_PHRASES = ("mas barato", "mas barata", "mas baratos", "mas baratas", "cheapest")
_UNDER = re.compile(
    r"\b(menos de|por debajo de|hasta|under|less than|below|up to)\s+"
    r"(?P<amount>\d+(?:[.,]\d+)?)\s*(€|euros?|eur)?"
)
# Free wifi or a gluten-free diet are things the assistant does not look up (D-050), not prices.
_NOT_A_PRICE = ("gluten free", "gluten-free", "free wifi", "wifi gratis", "wifi gratuito")
# Without a currency, "hasta 5" could be a time or a count: only a price word makes it one.
_PRICE_CONTEXT = ("cuesta", "cuestan", "precio", "pagar", "euro", "euros", "€", "cost", "price")


def wants_free(folded: str) -> bool:
    return contains_any(folded, FREE_PHRASES) and not contains_any(folded, _NOT_A_PRICE)


def price_under(folded: str) -> Decimal | None:
    match = _UNDER.search(folded)
    if match is None:
        return None
    if not match[3] and not any(word in folded for word in _PRICE_CONTEXT):
        return None
    return Decimal(match["amount"].replace(",", "."))


def wants_cheapest(folded: str) -> bool:
    return contains_any(folded, CHEAPEST_PHRASES)
