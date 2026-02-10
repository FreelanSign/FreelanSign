# apps/feedback/application/ports.py
from typing import Protocol

from apps.feedback.domain.entities import FeedbackEntity


class FeedbackRepository(Protocol):
    def create(self, *, user_id: int, entity: FeedbackEntity) -> FeedbackEntity: ...
