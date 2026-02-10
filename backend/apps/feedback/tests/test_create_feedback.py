# apps/feedback/tests/test_create_feedback.py
from unittest.mock import MagicMock

import pytest

from apps.feedback.application.dtos import CreateFeedbackInput
from apps.feedback.application.usecases.create_feedback import CreateFeedback
from apps.feedback.domain.entities import FeedbackCategory, FeedbackEntity
from apps.feedback.domain.policies import InvalidCategoryError, InvalidMessageLengthError


def _make_input(**overrides):
    defaults = {
        "category": "BUG",
        "message": "This is a valid bug report message",
        "user_email": "test@example.com",
        "page_url": "https://app.freelansign.fr/dashboard",
        "app_version": "v0.4.0",
        "user_agent": "Mozilla/5.0",
    }
    return CreateFeedbackInput(**{**defaults, **overrides})


def _make_entity(**overrides):
    defaults = {
        "id": "fake-uuid",
        "user_email": "test@example.com",
        "category": FeedbackCategory.BUG,
        "message": "This is a valid bug report message",
        "page_url": "https://app.freelansign.fr/dashboard",
        "app_version": "v0.4.0",
        "user_agent": "Mozilla/5.0",
    }
    return FeedbackEntity(**{**defaults, **overrides})


class TestCreateFeedback:
    def test_success(self):
        repo = MagicMock()
        saved_entity = _make_entity()
        repo.create.return_value = saved_entity

        uc = CreateFeedback(feedback_repository=repo)
        result = uc.execute(user_id=1, input_dto=_make_input())

        assert result == saved_entity
        repo.create.assert_called_once()

    def test_invalid_message_raises(self):
        repo = MagicMock()
        uc = CreateFeedback(feedback_repository=repo)

        with pytest.raises(InvalidMessageLengthError):
            uc.execute(user_id=1, input_dto=_make_input(message="short"))

        repo.create.assert_not_called()

    def test_invalid_category_raises(self):
        repo = MagicMock()
        uc = CreateFeedback(feedback_repository=repo)

        with pytest.raises(InvalidCategoryError):
            uc.execute(user_id=1, input_dto=_make_input(category="INVALID"))

        repo.create.assert_not_called()
