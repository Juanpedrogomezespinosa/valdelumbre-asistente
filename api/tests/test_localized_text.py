from app.domain.localized_text import Language, LocalizedText, ResolvedText


def test_spanish_is_returned_as_is() -> None:
    text = LocalizedText(es="Plaza Mayor", en="Main Square")

    assert text.resolve(Language.ES) == ResolvedText("Plaza Mayor", is_fallback=False)


def test_english_is_returned_when_available() -> None:
    text = LocalizedText(es="Plaza Mayor", en="Main Square")

    assert text.resolve(Language.EN) == ResolvedText("Main Square", is_fallback=False)


def test_missing_english_falls_back_to_spanish_and_says_so() -> None:
    text = LocalizedText(es="museo del aceite", en=None)

    assert text.resolve(Language.EN) == ResolvedText("museo del aceite", is_fallback=True)
