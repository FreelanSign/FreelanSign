# apps/quote/domain/services/totals.py
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
ZERO = Decimal("0.00")

def q2(v: Decimal) -> Decimal:
    return Decimal(str(v)).quantize(CENT, rounding=ROUND_HALF_UP)

def line_pre_tax_total(qty: Decimal, unit_price: Decimal, discount_abs: Decimal) -> Decimal:
    base = Decimal(str(qty)) * Decimal(str(unit_price)) - Decimal(str(discount_abs))
    if base < ZERO:
        base = ZERO
    return q2(base)

def line_tax_amount(pre_tax_total: Decimal, rate_pct: Decimal) -> Decimal:
    return q2(Decimal(str(pre_tax_total)) * (Decimal(str(rate_pct)) / Decimal("100")))

def compute_totals(lines: list[dict]) -> dict:
    subtotal = ZERO
    tax_total = ZERO
    for L in lines:
        ht = line_pre_tax_total(L["qty"], L["unit_price"], L.get("discount", ZERO))
        subtotal += ht
        tax_total += line_tax_amount(ht, L["tax_rate_pct"])   # <-- bonne clé
    subtotal, tax_total = q2(subtotal), q2(tax_total)
    return {"subtotal": subtotal, "tax_total": tax_total, "grand_total": q2(subtotal + tax_total)}
