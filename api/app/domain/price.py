from dataclasses import dataclass
from decimal import Decimal
from typing import Self


@dataclass(frozen=True)
class Price:
    min_eur: Decimal | None = None
    max_eur: Decimal | None = None

    def __post_init__(self) -> None:
        if self.min_eur is None or self.max_eur is None:
            if self.min_eur is not None or self.max_eur is not None:
                raise ValueError("A price needs both bounds or none")
            return
        if self.min_eur < 0:
            raise ValueError(f"A price cannot be negative: {self.min_eur}")
        if self.min_eur > self.max_eur:
            raise ValueError(f"The lower bound exceeds the upper: {self.min_eur}-{self.max_eur}")

    @classmethod
    def unknown(cls) -> Self:
        return cls()

    @classmethod
    def free(cls) -> Self:
        return cls(Decimal(0), Decimal(0))

    @classmethod
    def fixed(cls, amount: Decimal) -> Self:
        return cls(amount, amount)

    @classmethod
    def between(cls, low: Decimal, high: Decimal) -> Self:
        return cls(low, high)

    @property
    def is_unknown(self) -> bool:
        return self.min_eur is None

    @property
    def is_free(self) -> bool:
        return self.max_eur == 0
