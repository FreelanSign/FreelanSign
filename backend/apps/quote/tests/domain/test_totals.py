# apps/quote/tests/domain/test_totals.py
from decimal import Decimal

import pytest

from apps.quote.domain.services.totals import (
    compute_totals,
    line_pre_tax_total,
    line_tax_amount,
    q2,
)

D = Decimal


@pytest.mark.parametrize(
    "qty, unit, discount_pct, expected",
    [
        (D("1"), D("100"), D("0"), D("100.00")),  # simple
        (D("2"), D("10.50"), D("0"), D("21.00")),  # multiplication + arrondi
        (D("1"), D("100"), D("20"), D("80.00")),  # remise 20%
        (D("1"), D("100"), D("10"), D("90.00")),  # remise 10%
        (D("0.5"), D("99.99"), D("0"), D("50.00")),  # quantités fractionnaires
    ],
)
def test_line_pre_tax_total(qty, unit, discount_pct, expected):
    assert line_pre_tax_total(qty, unit, discount_pct) == expected


@pytest.mark.parametrize(
    "pre_tax, rate_pct, expected",
    [
        (D("100.00"), D("0.00"), D("0.00")),
        (D("100.00"), D("20.00"), D("20.00")),
        (D("49.99"), D("20.00"), D("10.00")),  # 9.998 -> 10.00 (arrondi HALF_UP)
        (D("80.00"), D("5.50"), D("4.40")),
    ],
)
def test_line_tax_amount(pre_tax, rate_pct, expected):
    assert line_tax_amount(pre_tax, rate_pct) == expected


def test_compute_totals_mixed_lines():
    lines = [
        {"qty": D("1"), "unit_price": D("100"), "discount": D("0"), "tax_rate_pct": D("20.00")},  # 100 HT, 20 TVA
        {"qty": D("2"), "unit_price": D("10"), "discount": D("0"), "tax_rate_pct": D("0.00")},  # 20 HT, 0 TVA
        {"qty": D("1"), "unit_price": D("50"), "discount": D("10"), "tax_rate_pct": D("5.50")},  # 45 HT (50 - 10%), 2.48 TVA
    ]
    totals = compute_totals(lines)
    assert totals["subtotal"] == D("165.00")
    assert totals["tax_total"] == D("22.48")
    assert totals["grand_total"] == D("187.48")
