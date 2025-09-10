"""Unit tests for keyword extraction functionality."""

from app.services.keywords import extract_top3_nouns_like


def test_keywords_basic() -> None:
    text = "OpenAI released a powerful model. The model helps developers build AI products. Developers love the model."
    kws = extract_top3_nouns_like(text)
    assert isinstance(kws, list)
    assert 1 <= len(kws) <= 3
    assert "model" in kws or "developers" in kws


def test_keywords_empty() -> None:
    assert extract_top3_nouns_like("") == []
    assert extract_top3_nouns_like("   ") == []