import pytest

from brac7.validation import ParticipantValidator, ValidationError


def test_valid_names():
    result = ParticipantValidator.validate_names(["Alice", "Bob", "Carol"])
    assert result == ["Alice", "Bob", "Carol"]


def test_too_few_names():
    with pytest.raises(ValidationError, match="Need at least 2"):
        ParticipantValidator.validate_names(["solo"])


def test_empty_names():
    with pytest.raises(ValidationError, match="Empty participant name"):
        ParticipantValidator.validate_names(["Alice", "", "Bob"])


def test_duplicate_names():
    with pytest.raises(ValidationError, match="Duplicate participant"):
        ParticipantValidator.validate_names(["Alice", "Bob", "Alice"])


def test_strips_whitespace():
    result = ParticipantValidator.validate_names(["  Alice  ", "  Bob  "])
    assert result == ["Alice", "Bob"]


def test_leading_trailing_whitespace_dedup():
    with pytest.raises(ValidationError, match="Duplicate"):
        ParticipantValidator.validate_names(["Alice", "  Alice  "])
