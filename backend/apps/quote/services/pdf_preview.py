# apps/quote/services/pdf_preview.py
from dataclasses import dataclass
from typing import Any, Dict

from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright

from apps.quote.domain.errors import (
    QuotePreviewEngineError,
    QuotePreviewError,
    QuotePreviewTemplateError,
    QuotePreviewValidationError,
)


@dataclass(frozen=True)
class QuotePreviewContext:
    """Données minimales pour le template PDF (pas d'accès DB ici)."""

    seller: Dict[str, Any]
    client: Dict[str, Any]
    meta: Dict[str, Any]
    lines: list[Dict[str, Any]]
    totals: Dict[str, Any]
    branding: Dict[str, Any] | None


def render_quote_html(context: QuotePreviewContext) -> str:
    """Rendre le HTML pour le template PDF."""
    try:
        return render_to_string(
            "quote/pdf/preview.html",
            {
                "seller": context.seller,
                "client": context.client,
                "meta": context.meta,
                "lines": context.lines,
                "totals": context.totals,
                "branding": context.branding or {},
            },
        )
    except TemplateDoesNotExist as e:
        raise QuotePreviewTemplateError(f"Template manquant: {e}")
    except Exception as e:
        raise QuotePreviewError(f"Erreur lors de la génération du HTML: {e}")


def html_to_pdf_bytes(html: str) -> bytes:
    """Convertir le HTML en PDF bytes avec Playwright."""
    try:
        with sync_playwright() as p:
            # Lancer le navigateur en mode headless
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Charger le HTML (wait_until='networkidle' attend que toutes les ressources soient chargées)
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
            return pdf_bytes

    except Exception as e:
        raise QuotePreviewEngineError(
            f"Erreur lors de la conversion HTML en PDF: {e.__class__.__name__}: {e}"
        ) from e


def render_quote_pdf(context: QuotePreviewContext) -> bytes:
    """Rendre le PDF pour le template PDF."""
    if not context.lines:
        raise QuotePreviewValidationError("Au moins une ligne est requise")
    if any(float(line["quantity"]) <= 0 for line in context.lines):
        raise QuotePreviewValidationError("La quantité doit être supérieure à 0")
    if any(float(line["unit_price"]) <= 0 for line in context.lines):
        raise QuotePreviewValidationError("Le prix unitaire doit être supérieur à 0")
    if any(float(line["tax_rate"]) < 0 or float(line["tax_rate"]) > 1.0 for line in context.lines):
        raise QuotePreviewValidationError("Le taux de taxe doit être compris entre 0 et 100")

    html = render_quote_html(context)
    return html_to_pdf_bytes(html)
