# apps/quote/application/ports/pdf_generator.py
from __future__ import annotations

from typing import Protocol


class PdfGenerator(Protocol):
    """
    Convert an HTML to PDF bytes. Does not know the ViewModel.
    The implementation (WeasyPrint/wkhtmltopdf) lives in adapters/.
    """

    def generate(self, *, html: str, base_url: str | None = None) -> bytes:
        """
        :param html: The HTML to convert.
        :param base_url: The base URL for the resources (images, css).
        :returns: The PDF bytes.
        """
        ...
