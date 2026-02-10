# backend/apps/email/application/usecases/prepare_quote_email.py
import logging
from dataclasses import dataclass
from uuid import UUID

from django.core.exceptions import PermissionDenied

from apps.email.application.dto.prepared_email_data import PreparedEmailData
from apps.email.application.ports.email_template_renderer import EmailTemplateRenderer
from apps.email.domain.entities.prepared_email import PreparedEmail
from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.user.models import User

logger = logging.getLogger(__name__)


@dataclass
class PrepareQuoteEmailCommand:
    """
    Input command object for PrepareQuoteEmail use case.

    Encapsulates all input data needed to perform the use case,
    including security context (requester) and localization.
    """

    quote_id: UUID
    requester: User
    locale: str = "fr"  # default locale


class PrepareQuoteEmail:
    """
    Use case: prepares a ready-to-send email from a quote.

    Orchestrates:
    - loading the quote (via QuoteRepository),
    - verifying access rights,
    - building a DTO for rendering (PreparedEmailData),
    - delegating to the EmailTemplateRenderer.

    Rationale:
    - Pure application logic, no I/O or framework coupling.
    - Respects Clean Architecture: all dependencies injected as ports.
    - Handles authorization, not authentication.
    """

    def __init__(self, quote_repo: QuoteRepository, renderer: EmailTemplateRenderer):
        self.quote_repo = quote_repo
        self.renderer = renderer

    def execute(self, command: PrepareQuoteEmailCommand) -> PreparedEmail:
        logger.debug(
            "Preparing quote email",
            extra={
                "quote_id": str(command.quote_id),
                "user_id": str(command.requester.id),
                "locale": command.locale,
            },
        )
        quote = self.quote_repo.get(quote_id=command.quote_id, requester_id=str(command.requester.id), include_lines=False)

        if quote.owner_id != command.requester.id:
            logger.warning(
                "Forbidden email preparation attempt",
                extra={
                    "quote_id": str(command.quote_id),
                    "user_id": str(command.requester.id),
                },
            )
            raise PermissionDenied("You do not have access to this quote.")

        dto = PreparedEmailData(
            client_name=quote.client.name,
            client_email=quote.client.email,
            quote_reference=quote.reference,
            quote_title=quote.title,
            quote_date=quote.issue_date,
            expiration_date=quote.valid_until,
            locale=command.locale,
            sender_name=quote.account.display_name,
        )

        email = PreparedEmail(
            to=dto.client_email,
            subject=f"Devis {dto.quote_reference} – {dto.quote_title}",
            body_plain=self.renderer.render_plain(dto),
            body_html=self.renderer.render_html(dto),
            template_version="v1.0",
        )

        logger.info(
            "Prepared quote email",
            extra={
                "quote_id": str(command.quote_id),
                "user_id": str(command.requester.id),
                "template_version": email.template_version,
            },
        )

        return email
