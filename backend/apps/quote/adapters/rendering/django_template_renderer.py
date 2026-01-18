# apps/quote/adapters/rendering/django_template_renderer.py

from __future__ import annotations

import logging
from types import SimpleNamespace

from django.template.loader import render_to_string

from apps.quote.application.dto.quote_viewmodels import QuoteViewModel
from apps.quote.application.ports.template_renderer import TemplateRenderer

log = logging.getLogger(__name__)


class DjangoTemplateRenderer(TemplateRenderer):
    def render(self, template_key: str, vm: QuoteViewModel, legal_terms_html: str | None = None) -> str:
        # AIDEV-NOTE: Diagnostic logs added to debug legal terms generation issue (#87)
        log.debug(
            "renderer.render.start template=%s has_legal_terms=%s legal_terms_length=%s",
            template_key,
            legal_terms_html is not None,
            len(legal_terms_html) if legal_terms_html else 0,
        )
        quote_map = {
            "reference": vm.meta.get("number"),
            "issue_date": vm.meta.get("date"),
            "valid_until": vm.meta.get("valid_until"),
            "payment_terms": vm.meta.get("payment_terms"),
            "currency": vm.meta.get("currency"),
            "language": vm.meta.get("language"),
            "title": vm.meta.get("title"),
            "note": vm.meta.get("note"),
            "payment_terms_text": vm.meta.get("payment_terms_text"),
        }

        lines = [
            {
                # "nouveau" jeu de clés
                "designation": l.designation,
                "description": l.description,
                "quantity": l.quantity,
                "unit_price": l.unit_price,
                "tax_rate": l.tax_rate_display / 100.0,  # 0..1 pour le template
                "tax_rate_display": l.tax_rate_display,  # % pour affichage
                "total_ht": l.total_ht,
                "discount": getattr(l, "discount", 0.0) or 0.0,
                # alias legacy
                "qty": l.quantity,
                "unit": l.unit_price,
                "tva": l.tax_rate_display,  # %
                "tax_rate_pct": l.tax_rate_display,
            }
            for l in vm.lines
        ]

        totals_raw = {
            "subtotal": float(vm.totals.subtotal or 0.0),
            "tax": float(vm.totals.tax or 0.0),
            "tax_total": float(vm.totals.tax or 0.0),  # alias pour le template document.html
            "grand_total": float(vm.totals.grand_total or 0.0),
            "total": float(vm.totals.grand_total or 0.0),  # alias pour le template document.html
        }
        totals_fmt = {
            "subtotal": f"{totals_raw['subtotal']:.2f}",
            "tax": f"{totals_raw['tax']:.2f}",
            "tax_total": f"{totals_raw['tax_total']:.2f}",  # alias pour le template document.html
            "grand_total": f"{totals_raw['grand_total']:.2f}",
            "total": f"{totals_raw['total']:.2f}",  # alias pour le template document.html
        }

        ctx = {
            "quote": quote_map,
            "seller": vm.seller,
            "client": vm.client,
            "meta": vm.meta,
            "lines": lines,
            "totals": totals_fmt,  # ⬅️ le template lit `totals.*` => prêt à afficher
            "totals_raw": totals_raw,  # ⬅️ dispo si besoin de calculs ailleurs
            "branding": vm.branding or {},
            "is_download": False,
            "legal_terms_html": legal_terms_html,  # Phase 7: legal terms for PDF
        }

        # Compatibilité "vm.*" si des templates l'utilisent
        ctx["vm"] = SimpleNamespace(
            seller=ctx["seller"],
            client=ctx["client"],
            meta=ctx["meta"],
            lines=[SimpleNamespace(**l) for l in lines],
            totals=SimpleNamespace(**totals_fmt),
            totals_raw=SimpleNamespace(**totals_raw),
            branding=ctx["branding"],
            quote=SimpleNamespace(**quote_map),
        )

        # AIDEV-NOTE: Log context to confirm legal_terms_html is passed to template
        log.debug(
            "renderer.render.context_prepared has_legal_terms_in_ctx=%s",
            "legal_terms_html" in ctx and ctx["legal_terms_html"] is not None,
        )

        return render_to_string(template_key, ctx)
