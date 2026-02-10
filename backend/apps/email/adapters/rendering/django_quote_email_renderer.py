# backend/apps/email/adapters/rendering/django_quote_email_renderer.py
import logging

import bleach
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from apps.email.application.dto.prepared_email_data import PreparedEmailData
from apps.email.application.ports.email_template_renderer import EmailTemplateRenderer

logger = logging.getLogger(__name__)


class DjangoQuoteEmailRenderer(EmailTemplateRenderer):
    """
    Adapter rendering email content using Django templates.

    Responsibilities:
    - Select localized templates (based on PreparedEmailData.locale).
    - Render both plain text and HTML versions.
    - Sanitize HTML output to prevent injection (bleach).

    Rationale:
    - Keeps business logic (UC) independent of rendering tech.
    - Localisation-ready (locale-based template paths).
    - Defensive HTML sanitation for safety.
    """

    def render_plain(self, data: PreparedEmailData) -> str:
        # AIDEV-NOTE: Force French locale as only supported language
        locale = "fr"
        try:
            return render_to_string(f"emails/quote_{locale}.txt", {"data": data})
        except TemplateDoesNotExist as e:
            logger.error(
                "Missing email template",
                extra={
                    "template": f"emails/quote_{locale}.txt",
                    "quote_id": str(data.quote_reference),
                    "client_email": data.client_email,
                    "locale": locale,
                },
            )
            raise
        except Exception as e:
            logger.error("Error rendering plain text email", exc_info=e)
            raise

    def render_html(self, data: PreparedEmailData) -> str:
        # AIDEV-NOTE: Force French locale as only supported language
        locale = "fr"
        try:
            raw_html = render_to_string(f"emails/quote_{locale}.html", {"data": data})
            return bleach.clean(raw_html, tags=["p", "b", "strong", "em", "ul", "ol", "li", "br"], attributes={}, strip=True)
        except TemplateDoesNotExist as e:
            logger.error(
                "Missing email template",
                extra={
                    "template": f"emails/quote_{locale}.txt",
                    "quote_id": str(data.quote_reference),
                    "client_email": data.client_email,
                    "locale": locale,
                },
            )
            return "<p>Erreur de génération d'email.</p>"
        except Exception as e:
            logger.error("Error rendering HTML email", exc_info=e)
            return "<p>Erreur de génération d'email.</p>"
