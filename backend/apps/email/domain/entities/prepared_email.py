# backend/apps/email/domain/entities/prepared_email.py

from dataclasses import dataclass


@dataclass(frozen=True)
class PreparedEmail:
    """
    Value Object representing a fully rendered email content.

    Contains both plain text and HTML versions for accessibility and flexibility.
    Output of the PrepareQuoteEmail use case.

    Rationale:
    - Immutable (Value Object).
    - Renderer is responsible for converting business data to formatted content.
    - No business logic inside — only data transport for final email.

    Used directly in the API response.
    """

    to: str
    subject: str
    body_plain: str
    body_html: str
    template_version: str
