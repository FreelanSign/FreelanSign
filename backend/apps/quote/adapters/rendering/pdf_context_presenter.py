# apps/quote/adapters/rendering/pdf_context_presenter.py
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Mapping, Sequence

from apps.quote.application.dto.quote_viewmodels import QuoteViewModel


def _get(obj: Any, key: str, default=None):
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _line_to_dict(line: Any) -> dict:
    if isinstance(line, Mapping):
        tr_disp = line.get("tax_rate_display")
        if tr_disp is None and line.get("tax_rate") is not None:
            tr_disp = float(line["tax_rate"]) * 100.0
        return {
            "designation": line.get("designation"),
            "description": line.get("description"),
            "quantity": line.get("quantity"),
            "unit_price": line.get("unit_price"),
            "tax_rate": (tr_disp or 0.0) / 100.0,
            "tax_rate_display": tr_disp or 0.0,
            "total_ht": line.get("total_ht"),
            "discount": line.get("discount", 0.0) or 0.0,
        }
    # Objet LineVM
    tr_disp = float(getattr(line, "tax_rate_display"))
    return {
        "designation": getattr(line, "designation"),
        "description": getattr(line, "description"),
        "quantity": getattr(line, "quantity"),
        "unit_price": getattr(line, "unit_price"),
        "tax_rate": tr_disp / 100.0,
        "tax_rate_display": tr_disp,
        "total_ht": getattr(line, "total_ht"),
        "discount": getattr(line, "discount", 0.0) or 0.0,
    }


def preview_context(vm: QuoteViewModel | dict, *, is_download: bool = False) -> dict:
    seller = _get(vm, "seller") or {}
    client = _get(vm, "client") or {}
    meta = _get(vm, "meta") or {}
    lines: Sequence[Any] = _get(vm, "lines") or []
    totals = _get(vm, "totals") or {}

    if not isinstance(totals, Mapping):
        totals = {
            "subtotal": getattr(totals, "subtotal", 0.0),
            "tax": getattr(totals, "tax", 0.0),
            "grand_total": getattr(totals, "grand_total", 0.0),
        }

    lines_dict = [_line_to_dict(l) for l in lines]

    ctx = {
        "quote": {
            "reference": meta.get("number"),
            "issue_date": meta.get("date"),
            "valid_until": meta.get("valid_until"),
            "payment_terms": meta.get("payment_terms"),
            "currency": meta.get("currency"),
            "language": meta.get("language"),
            "title": meta.get("title"),
            "note": meta.get("note"),
            "payment_terms_text": meta.get("payment_terms_text"),
        },
        "seller": seller,
        "client": client,
        "meta": meta,
        "lines": lines_dict,
        "totals": totals,
        "branding": _get(vm, "branding") or {},
        "is_download": is_download,
    }

    # 🔑 Compat: expose aussi un namespace 'vm' pour les templates qui font vm.seller etc.
    ctx["vm"] = SimpleNamespace(
        seller=seller,
        client=client,
        meta=meta,
        lines=[SimpleNamespace(**ld) for ld in lines_dict],
        totals=SimpleNamespace(**totals),
        branding=ctx["branding"],
        quote=SimpleNamespace(**ctx["quote"]),
    )
    return ctx
