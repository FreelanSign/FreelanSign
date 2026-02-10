# apps/feedback/adapters/django_feedback_repository.py
from apps.feedback.domain.entities import FeedbackCategory, FeedbackEntity
from apps.feedback.models import Feedback


class DjangoFeedbackRepository:
    def create(self, *, user_id: int, entity: FeedbackEntity) -> FeedbackEntity:
        obj = Feedback.objects.create(
            user_id=user_id,
            category=entity.category.value,
            message=entity.message,
            email=entity.user_email,
            page_url=entity.page_url,
            app_version=entity.app_version,
            user_agent=entity.user_agent,
        )
        return FeedbackEntity(
            id=str(obj.id),
            user_email=obj.email,
            category=FeedbackCategory(obj.category),
            message=obj.message,
            page_url=obj.page_url,
            app_version=obj.app_version,
            user_agent=obj.user_agent,
            created_at=obj.created_at,
        )
