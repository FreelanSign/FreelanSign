# apps/feedback/application/usecases/create_feedback.py
import logging

from apps.feedback.application.dtos import CreateFeedbackInput
from apps.feedback.application.ports import FeedbackRepository
from apps.feedback.domain.entities import FeedbackEntity
from apps.feedback.domain.policies import validate_category, validate_message

logger = logging.getLogger(__name__)


class CreateFeedback:
    def __init__(self, *, feedback_repository: FeedbackRepository):
        self.feedback_repository = feedback_repository

    def execute(self, *, user_id: int, input_dto: CreateFeedbackInput) -> FeedbackEntity:
        validated_message = validate_message(input_dto.message)
        validated_category = validate_category(input_dto.category)

        entity = FeedbackEntity(
            id=None,
            user_email=input_dto.user_email,
            category=validated_category,
            message=validated_message,
            page_url=input_dto.page_url,
            app_version=input_dto.app_version,
            user_agent=input_dto.user_agent,
        )

        saved = self.feedback_repository.create(user_id=user_id, entity=entity)
        logger.info("Feedback created: category=%s user=%s", validated_category.value, input_dto.user_email)

        return saved
