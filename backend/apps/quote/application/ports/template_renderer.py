# apps/quote/application/ports/template_renderer.py
from __future__ import annotations

from apps.quote.application.dto.quote_viewmodels import QuoteViewModel


class TemplateRenderer:
    """Interface for a template renderer. No implementation is provided here."""

    def render(
        self,
        template_key: str,
        vm: QuoteViewModel,
        legal_terms_html: str | None = None,
        is_download: bool = False,
    ) -> str:
        """
        :param template_key: The key of the template to render.
        :param vm: The view model to render.
        :param legal_terms_html: Optional HTML for legal terms (CGV).
        :param is_download: True for final download (no watermark), False for preview (with watermark).

        :returns: The rendered template.
        """
        ...
