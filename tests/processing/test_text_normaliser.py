from services.processing.normalization.text_normaliser import TextNormalizer

def test_clean_text():
    raw = """
    arXiv:2304.12345

    This is a sample text - 
    with hyphenation across lines.

    Page 2 of 10

    Some equations: $E=mc^2$
    """

    normalizer = TextNormalizer(remove_latex=True)
    cleaned = normalizer.clean(raw)

    assert "arXiv" not in cleaned
    assert "Page 2 of 10" not in cleaned
    assert "$" not in cleaned
    assert "hyphenation across" in cleaned
