# apps/quote/services/pdf_preview.py
from dataclasses import dataclass
from typing import Any, Dict
import os
from pathlib import Path
import shutil
import subprocess

from django.conf import settings
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
import pdfkit

from apps.quote.domain.errors import (
    QuotePreviewEngineError,
    QuotePreviewError,
    QuotePreviewSecurityError,
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
    """Convertir le HTML en PDF bytes avec wkhtmltopdf."""
    try:
        # Configuration wkhtmltopdf
        config = None
        wkhtmltopdf_cfg = getattr(settings, "WKHTMLTOPDF_PATH", None)

        if wkhtmltopdf_cfg:
            wk_path = str(wkhtmltopdf_cfg)
            if not Path(wk_path).exists():
                raise QuotePreviewEngineError(
                    f"wkhtmltopdf n'est pas trouvé au chemin: {wk_path}. "
                    "Vérifiez l'installation ou la variable WKHTMLTOPDF_PATH."
                )
            config = pdfkit.configuration(wkhtmltopdf=wk_path)
        else:
            found = shutil.which("wkhtmltopdf")
            if found:
                config = pdfkit.configuration(wkhtmltopdf=found)
            else:
                raise QuotePreviewEngineError(
                    "wkhtmltopdf n'est pas trouvé dans le PATH. "
                    "Vérifiez l'installation ou la variable WKHTMLTOPDF_PATH."
                )
        # Options PDF
        options = {
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'no-outline': None,
            'enable-local-file-access': None,
            'print-media-type': None,
            'load-error-handling': 'ignore',
        }

        return pdfkit.from_string(html, False, options=options, configuration=config)
    except OSError as e:
        if 'No wkhtmltopdf executable found' in str(e):
            raise QuotePreviewEngineError(
                f"wkhtmltopdf n'est pas trouvé au chemin: {getattr(settings, 'WKHTMLTOPDF_PATH', 'Non défini')}."
                "Vérifiez l'installation ou la variable WKHTMLTOPDF_PATH."
            ) from e
        raise QuotePreviewEngineError(f"Erreur système: {e}") from e
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
