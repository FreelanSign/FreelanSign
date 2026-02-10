# apps/feedback/application/dtos.py
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateFeedbackInput:
    category: str
    message: str
    user_email: str
    page_url: str
    app_version: str
    user_agent: str
