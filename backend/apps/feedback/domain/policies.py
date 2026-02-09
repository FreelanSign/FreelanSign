# apps/feedback/domain/policies.py

from apps.feedback.domain.entities import FeedbackCategory

MIN_MESSAGE_LENGTH = 10
MAX_MESSAGE_LENGTH = 2000

VALID_CATEGORIES = {c.value for c in FeedbackCategory}


class InvalidMessageLengthError(Exception):
    pass


class InvalidCategoryError(Exception):
    pass


def validate_message(message: str) -> str:
    stripped = message.strip()
    length = len(stripped)
    if length < MIN_MESSAGE_LENGTH or length > MAX_MESSAGE_LENGTH:
        raise InvalidMessageLengthError(
            f"Message must be between {MIN_MESSAGE_LENGTH} and {MAX_MESSAGE_LENGTH} characters (got {length})"
        )
    return stripped


def validate_category(category: str) -> FeedbackCategory:
    upper = category.upper()
    if upper not in VALID_CATEGORIES:
        raise InvalidCategoryError(f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}")
    return FeedbackCategory(upper)
