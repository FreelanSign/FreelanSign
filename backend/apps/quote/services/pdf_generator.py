# apps/quote/services/pdf_generator.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright

from apps.quote.models import Quote


class QuotePdfError(Exception):
    """Exception raised when there is an error generating the PDF."""

    pass


@dataclass(frozen=True)
class QuotePdfOptions:
    template: str = "quote/pdf/document.html"
    filename_prefix: str = "Devis"


def _build_filename(quote: Quote, prefix: str) -> str:
    """Build a filename for the PDF based on the quote and the prefix."""
    # ex : Devis-FS-2025-0012-2025-10-18.pdf
    ref = getattr(quote, "reference", f"QUOTE-{quote.pk}")
    date_str = datetime.now().strftime("%Y-%m-%d")
    return f"{prefix}-{ref}-{date_str}.pdf".replace(" ", "-")


def render_quote_pdf(quote_id: int | str, *, options: QuotePdfOptions = QuotePdfOptions()) -> tuple[bytes, str]:
    """Render a quote PDF."""
    try:
        quote = Quote.objects.select_related("client").get(pk=quote_id)
    except Quote.DoesNotExist as e:
        raise QuotePdfError(f"Devis introuvable: {quote_id}") from e

    # Contexte : reprends ce que tu utilises déjà en preview (seller, client, meta, lines, totals, branding)
    try:
        context = {
            "quote": quote,
            "client": getattr(quote, "client", None),
            "meta": {
                "number": getattr(quote, "reference", f"QUOTE-{quote.pk}"),
                "date": quote.issue_date,
                "valid_until": quote.valid_until,
                "payment_terms": quote.payment_terms,
                "currency": quote.currency,
                "language": quote.language,
                "title": quote.title,
            },
            "lines": quote.items.all(),
            "totals": {
                "subtotal": quote.subtotal,
                "tax_total": quote.tax_total,
                "discount_total": quote.discount_total,
                "total": quote.total,
            },
            "branding": getattr(quote, "branding", None),
            "is_download": True,
        }
    except Exception as e:
        raise QuotePdfError(f"Erreur lors de la construction du contexte: {e}") from e

    # 1) Rendu HTML
    try:
        html = render_to_string(options.template, context)
    except Exception as e:
        raise QuotePdfError(f"Erreur lors du rendu HTML: {e}") from e

    # 2) Conversion HTML en PDF avec Playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Charger le HTML
            page.set_content(html, wait_until='networkidle')

            # Générer le PDF
            pdf_bytes = page.pdf(
                format='A4',
                margin={
                    'top': '10mm',
                    'right': '10mm',
                    'bottom': '10mm',
                    'left': '10mm'
                },
                print_background=True  # Important pour les couleurs de fond et images
            )

            browser.close()

    except Exception as e:
        raise QuotePdfError(f"Erreur lors de la conversion HTML en PDF: {e}") from e

    filename = _build_filename(quote, options.filename_prefix)
    return pdf_bytes, filename
