# apps/quote/application/ports/template_renderer.py
from __future__ import annotations

from apps.quote.application.dto.quote_viewmodels import QuoteViewModel


class TemplateRenderer:
    """Interface for a template renderer. No implementation is provided here."""

    def render(self, *, template_key: str, vm: QuoteViewModel) -> str:
        """
        :param template_key: The key of the template to render.
        :param vm: The view model to render.

        :returns: The rendered template.
        """
        ...
