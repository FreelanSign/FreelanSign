# apps/quote/services/pdf_generator.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string
import pdfkit
import os

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

    # 2) Conversion HTML en PDF avec wkhtmltopdf
    try:
        # Configuration wkhtmltopdf
        config = None
        wkhtmltopdf_path = getattr(settings, 'WKHTMLTOPDF_PATH', None)

        if wkhtmltopdf_path and os.path.exists(wkhtmltopdf_path):
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # Options PDF
        options_pdf = {
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'no-outline': None,
            'enable-local-file-access': None,  # Pour charger les CSS/images locales,
            'print-media-type': None,
            'load-error-handling': 'ignore',
        }

        pdf_bytes = pdfkit.from_string(html, False, options=options_pdf, configuration=config)

    except OSError as e:
        if 'No wkhtmltopdf executable found' in str(e):
            raise QuotePdfError(
                f"wkhtmltopdf n'est pas trouvé. Chemin configuré: {getattr(settings, 'WKHTMLTOPDF_PATH', 'Non défini')}. "
                "Vérifiez l'installation ou la variable WKHTMLTOPDF_PATH."
            ) from e
        raise QuotePdfError(f"Erreur système lors de la génération du PDF: {e}") from e
    except Exception as e:
        raise QuotePdfError(f"Erreur lors de la conversion HTML en PDF: {e}") from e

    filename = _build_filename(quote, options.filename_prefix)
    return pdf_bytes, filename
