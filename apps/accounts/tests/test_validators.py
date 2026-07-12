"""Tests for custom password validators."""

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.validators import LetterAndNumberValidator


@pytest.fixture
def validator():
    return LetterAndNumberValidator()


class TestLetterAndNumberValidator:
    """Tests for LetterAndNumberValidator."""

    def test_valid_password_letters_and_numbers(self, validator):
        """Password with both letters and numbers passes."""
        validator.validate("abc123xyz")

    def test_valid_password_single_letter_and_number(self, validator):
        """Minimum case: one letter and one number."""
        validator.validate("a1")

    def test_valid_password_mixed_case_with_numbers(self, validator):
        """Mixed case letters with numbers."""
        validator.validate("AbCd1234")

    def test_valid_password_with_special_chars(self, validator):
        """Letters, numbers, and special characters."""
        validator.validate("p@ssw0rd!")

    def test_invalid_only_letters(self, validator):
        """Only letters — no number — fails."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("abcdefgh")
        assert exc_info.value.code == "letter_and_number_required"

    def test_invalid_only_numbers(self, validator):
        """Only numbers — no letter — fails."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("12345678")
        assert exc_info.value.code == "letter_and_number_required"

    def test_invalid_only_special_chars(self, validator):
        """Only special characters — fails."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("!@#$%^&*")
        assert exc_info.value.code == "letter_and_number_required"

    def test_invalid_empty_string(self, validator):
        """Empty string fails."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("")
        assert exc_info.value.code == "letter_and_number_required"

    def test_get_help_text(self, validator):
        """Help text is descriptive."""
        help_text = validator.get_help_text()
        assert "letter" in help_text.lower()
        assert "number" in help_text.lower()
