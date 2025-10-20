# apps/quote/domain/services/totals.py
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
ZERO = Decimal("0.00")

def q2(v: Decimal) -> Decimal:
    """ Quantize a value to 2 decimal places.

    Args:
        v: The value to quantize.

    Returns:
        The quantized value.
    """
    return v.quantize(CENT, rounding=ROUND_HALF_UP)

def line_pre_tax_total(qty: Decimal, unit_price: Decimal, discount_abs: Decimal) -> Decimal:
    """ Compute the pre-tax total for a line.
    Args:
        qty: The quantity of the line.
        unit_price: The unit price of the line.
        discount_abs: The absolute discount of the line.

    Returns:
        The pre-tax total for the line.
    """
    base = Decimal(str(qty)) * Decimal(str(unit_price)) - Decimal(str(discount_abs))
    if base < ZERO:
        base = ZERO
    return q2(base)

def line_tax_amount(pre_tax_total: Decimal, rate_pct: Decimal) -> Decimal:
    """ Compute the tax amount for a line.
    Args:
        pre_tax_total: The pre-tax total of the line.
        rate_pct: The tax rate of the line (as percentage).

    Returns:
        The tax amount for the line.
    """
    return q2(Decimal(str(pre_tax_total)) * Decimal(str(rate_pct)) / Decimal("100"))

def compute_totals(lines: list[dict]) -> dict:
    """ Compute the totals for a list of lines.
    Args:
        lines: The list of lines.

    Returns:
        A dictionary with the subtotal, tax_total and grand_total.\n
        The subtotal is the sum of the pre-tax totals of the lines.\n
        The tax_total is the sum of the tax amounts of the lines.\n
        The grand_total is the sum of the subtotal and the tax_total.
    """
    subtotal = ZERO
    tax_total = ZERO
    for line in lines:
        ht = line_pre_tax_total(line["qty"], line["unit_price"], line.get("discount", ZERO))
        subtotal += ht
        tax_total += line_tax_amount(ht, line["tax_rate"])
    subtotal, tax_total = q2(subtotal), q2(tax_total)
    return {
        "subtotal": subtotal,
        "tax_total": tax_total,
        "grand_total": subtotal + tax_total,
    }
