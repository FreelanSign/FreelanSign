# apps/quote/tests/application/test_generate_preview.py
from decimal import Decimal

import pytest

from apps.quote.application.dto.quote_inputs import LineItemInputDTO, PreviewPayloadDTO
from apps.quote.application.usecases.generate_preview import generate_preview

D = Decimal


def _mk_line(desc, qty, unit, *, discount=None, tax_rate_pct=None, tax_rate_fraction=None, description=None):
    """
    Helper:
      - tax_rate_pct: ex 20 (pour 20%)
      - tax_rate_fraction: ex 0.2 (pour 20%)
    """
    rate = None
    if tax_rate_pct is not None and tax_rate_fraction is not None:
        raise AssertionError("Provide either tax_rate_pct or tax_rate_fraction, not both.")
    if tax_rate_pct is not None:
        rate = D(str(tax_rate_pct))
    if tax_rate_fraction is not None:
        # la view convertira la fraction en % avant de passer au DTO
        rate = D(str(tax_rate_fraction * 100))
    return LineItemInputDTO(
        designation=desc,  # was 'description', now 'designation' (item name)
        qty=D(str(qty)),
        unit_price=D(str(unit)),
        discount=(D(str(discount)) if discount is not None else None),
        tax_rate_pct=rate,
        description=description,  # optional detailed description
    )


def _mk_payload(lines, *, owner_vat_exempt=False, owner_default_rate_pct=20, client_country="FR"):
    return PreviewPayloadDTO(
        seller={"name": "Seller SAS"},
        client={"name": "Client", "country": client_country},
        meta={"ref": "Q-001"},
        lines=lines,
        branding=None,
        owner_vat_exempt=owner_vat_exempt,
        owner_default_rate_pct=D(str(owner_default_rate_pct)),
        client_country=client_country,
    )


def test_generate_preview_with_percent_rates():
    payload = _mk_payload(
        [
            _mk_line("L1", qty=1, unit=100, discount=0, tax_rate_pct=20),
            _mk_line("L2", qty=2, unit=10, discount=0, tax_rate_pct=0),
            _mk_line("L3", qty=1, unit=50, discount=10, tax_rate_pct=5.5),
        ],
        owner_vat_exempt=False,
        owner_default_rate_pct=20,
        client_country="ES",  # hors FR pour ne pas déclencher la règle FR stricte
    )
    vm = generate_preview(payload)

    # Lignes
    assert len(vm.lines) == 3
    assert vm.lines[0].designation == "L1"
    assert vm.lines[0].tax_rate_display == 20.0
    # Totaux (approx sur float)
    assert vm.totals.subtotal == pytest.approx(160.0)
    assert vm.totals.tax == pytest.approx(22.2)
    assert vm.totals.grand_total == pytest.approx(182.2)


def test_generate_preview_fraction_input_is_normalized_to_percent():
    payload = _mk_payload(
        [
            _mk_line("L1", qty=1, unit=100, tax_rate_fraction=0.2),
        ],
        owner_vat_exempt=False,
        owner_default_rate_pct=20,
        client_country="ES",
    )
    vm = generate_preview(payload)
    assert vm.lines[0].tax_rate_display == 20.0
    assert vm.totals.subtotal == pytest.approx(100.0)
    assert vm.totals.tax == pytest.approx(20.0)
    assert vm.totals.grand_total == pytest.approx(120.0)


def test_generate_preview_owner_exempt_forces_zero_rate():
    payload = _mk_payload(
        [
            _mk_line("L1", qty=1, unit=100, tax_rate_pct=20),  # fourni mais devrait devenir 0
        ],
        owner_vat_exempt=True,
        owner_default_rate_pct=20,
        client_country="FR",
    )
    vm = generate_preview(payload)
    assert vm.lines[0].tax_rate_display == 0.0
    assert vm.totals.subtotal == pytest.approx(100.0)
    assert vm.totals.tax == pytest.approx(0.0)
    assert vm.totals.grand_total == pytest.approx(100.0)


def test_generate_preview_fr_client_requires_vat_when_owner_not_exempt():
    payload = _mk_payload(
        [
            _mk_line("L1", qty=1, unit=100, tax_rate_pct=0),  # interdit pour client FR si owner taxable
            _mk_line("L2", qty=1, unit=100, tax_rate_pct=20),
        ],
        owner_vat_exempt=False,
        owner_default_rate_pct=20,
        client_country="FR",
    )
    with pytest.raises(Exception):  # TaxPolicyError remontée par le use case
        generate_preview(payload)


def test_generate_preview_uses_owner_default_when_rate_missing():
    payload = _mk_payload(
        [
            _mk_line("L1", qty=1, unit=100, tax_rate_pct=None),  # manquant -> fallback owner default (20%)
        ],
        owner_vat_exempt=False,
        owner_default_rate_pct=20,
        client_country="ES",
    )
    vm = generate_preview(payload)
    assert vm.lines[0].tax_rate_display == 20.0
    assert vm.totals.tax == pytest.approx(20.0)
