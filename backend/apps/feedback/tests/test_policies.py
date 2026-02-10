# apps/feedback/tests/test_policies.py
import pytest

from apps.feedback.domain.entities import FeedbackCategory
from apps.feedback.domain.policies import (
    InvalidCategoryError,
    InvalidMessageLengthError,
    validate_category,
    validate_message,
)


class TestValidateMessage:
    def test_valid_message(self):
        result = validate_message("This is a valid feedback message")
        assert result == "This is a valid feedback message"

    def test_strips_whitespace(self):
        result = validate_message("   This is a valid message   ")
        assert result == "This is a valid message"

    def test_too_short(self):
        with pytest.raises(InvalidMessageLengthError):
            validate_message("Short")

    def test_exactly_min_length(self):
        result = validate_message("A" * 10)
        assert len(result) == 10

    def test_too_long(self):
        with pytest.raises(InvalidMessageLengthError):
            validate_message("A" * 2001)

    def test_exactly_max_length(self):
        result = validate_message("A" * 2000)
        assert len(result) == 2000

    def test_empty_string(self):
        with pytest.raises(InvalidMessageLengthError):
            validate_message("")

    def test_whitespace_only(self):
        with pytest.raises(InvalidMessageLengthError):
            validate_message("         ")


class TestValidateCategory:
    def test_valid_bug(self):
        assert validate_category("BUG") == FeedbackCategory.BUG

    def test_valid_suggestion(self):
        assert validate_category("SUGGESTION") == FeedbackCategory.SUGGESTION

    def test_valid_question(self):
        assert validate_category("QUESTION") == FeedbackCategory.QUESTION

    def test_valid_kudos(self):
        assert validate_category("KUDOS") == FeedbackCategory.KUDOS

    def test_case_insensitive(self):
        assert validate_category("bug") == FeedbackCategory.BUG
        assert validate_category("Suggestion") == FeedbackCategory.SUGGESTION

    def test_invalid_category(self):
        with pytest.raises(InvalidCategoryError):
            validate_category("INVALID")
