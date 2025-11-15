# backend/apps/email/application/ports/email_template_renderer.py
from abc import ABC, abstractmethod

from apps.email.application.dto.prepared_email_data import PreparedEmailData


class EmailTemplateRenderer(ABC):
    """
    Port interface for rendering email content from structured data.

    Rationale:
    - Separates rendering concerns from business logic (SRP).
    - Enables flexible strategies (plain text, HTML, markdown, localized templates).
    - Respects Clean Arch: Renderer is an outbound adapter (secondary port).

    Used by the PrepareQuoteEmail use case to produce the final PreparedEmail.
    """

    @abstractmethod
    def render_plain(self, data: PreparedEmailData) -> str:
        """Return a plain-text version of the email body."""
        raise NotImplementedError

    @abstractmethod
    def render_html(self, data: PreparedEmailData) -> str:
        """Return an HTML version of the email body (sanitized)."""
        raise NotImplementedError
