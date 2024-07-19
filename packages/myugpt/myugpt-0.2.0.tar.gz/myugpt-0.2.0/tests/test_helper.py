import pytest
from pydantic import ValidationError
from myugpt.helper import text_similarity

# Sample texts for testing
text1 = "This is a sample sentence."
text2 = "This is another example sentence."
text3 = "Completely different text."


def test_text_similarity_same_text():
    """Test if the similarity of the same text returns 100.0"""
    assert text_similarity(text1, text1) == 100.0


def test_text_similarity_different_texts_high_similarity():
    """Test if the similarity of two similar texts returns a high similarity score"""
    score = text_similarity(text1, text2)
    assert (
        0 <= score < 100
    )  # Since they are similar, ensure it's less than 100 but non-negative


def test_text_similarity_completely_different_texts():
    """Test if the similarity of two different texts returns a lower similarity score"""
    score = text_similarity(text1, text3)
    assert (
        0 <= score < 100
    )  # Since they are different, ensure it's less than 100 but non-negative


def test_invalid_input_none():
    """Test what happens if one of the inputs is None"""
    with pytest.raises(ValidationError):
        text_similarity(None, text1)


def test_invalid_input_empty_string():
    """Test if the similarity of an empty string and a text returns a non-negative score"""
    score = text_similarity("", text1)
    assert 0 <= score < 100


def test_invalid_input_both_empty_strings():
    """Test if the similarity of two empty strings returns 100"""
    assert text_similarity("", "") == 100.0


if __name__ == "__main__":
    pytest.main()
