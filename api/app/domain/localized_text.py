from dataclasses import dataclass
from enum import StrEnum


class Language(StrEnum):
    ES = "es"
    EN = "en"


@dataclass(frozen=True)
class ResolvedText:
    text: str
    is_fallback: bool


@dataclass(frozen=True)
class LocalizedText:
    es: str
    en: str | None = None

    def resolve(self, language: Language) -> ResolvedText:
        if language is Language.EN and self.en is not None:
            return ResolvedText(self.en, is_fallback=False)
        return ResolvedText(self.es, is_fallback=language is not Language.ES)
