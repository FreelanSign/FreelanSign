# apps/feedback/domain/entities.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class FeedbackCategory(str, Enum):
    BUG = "BUG"
    SUGGESTION = "SUGGESTION"
    QUESTION = "QUESTION"
    KUDOS = "KUDOS"


@dataclass(frozen=True)
class FeedbackEntity:
    id: Optional[str]
    user_email: str
    category: FeedbackCategory
    message: str
    page_url: str
    app_version: str
    user_agent: str
    created_at: Optional[datetime] = None
