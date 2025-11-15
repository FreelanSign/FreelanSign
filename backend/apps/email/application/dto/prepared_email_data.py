# backend/apps/email/application/dto/prepared_email_data.py
from dataclasses import dataclass
from datetime import date


@dataclass
class PreparedEmailData:
    """
    Structured DTO used as input for rendering the prepared email.
    This object contains only pure business data — no formatting or presentation.

    Rationale:
    - Clean separation between business logic (data) and presentation (templating).
    - Supports multiple renderers (plain text, HTML, future markdown, etc.).
    - Aligned with SRP (email content preparation ≠ formatting).

    Injected into EmailTemplateRenderer.
    """

    client_name: str
    client_email: str
    quote_reference: str
    quote_title: str
    quote_date: date
    expiration_date: date
    locale: str  # e.g. "fr" or "en"
