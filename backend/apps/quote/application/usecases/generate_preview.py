# apps/quote/application/usecases/generate_preview.py
from __future__ import annotations

from decimal import Decimal

from apps.quote.application.dto.quote_inputs import PreviewPayloadDTO
from apps.quote.application.dto.quote_viewmodels import LineVM, QuoteViewModel, TotalsVM
from apps.quote.domain.policies.tax_policy import effective_rate_for_line, validate_client_vat_rule
from apps.quote.domain.services.totals import compute_totals


def generate_preview(dto: PreviewPayloadDTO) -> QuoteViewModel:
    """Generate a preview of a quote.

    Args:
        dto: The preview payload DTO.

    Returns:
        The preview quote view model.
    """
    lines_pct: list[Decimal] = []
    normalized_lines = []

    for line in dto.lines:
        rate_pct = effective_rate_for_line(
            line.tax_rate_pct,
            owner_vat_exempt=dto.owner_vat_exempt,
            owner_default_rate_pct=dto.owner_default_rate_pct,
        )
        lines_pct.append(rate_pct)
        normalized_lines.append(
            {
                "qty": line.qty,
                "unit_price": line.unit_price,
                "discount": line.discount or Decimal("0.00"),
                "tax_rate_pct": rate_pct,  # clé attendue par compute_totals
                "designation": line.description or "",
                "description": None,
            }
        )

    # Règle FR (client FR + owner taxable => pas de lignes à 0)
    validate_client_vat_rule(dto.client_country, dto.owner_vat_exempt, lines_pct)

    totals = compute_totals(normalized_lines)

    vm_lines = []
    for L in normalized_lines:
        total_ht = (L["qty"] * L["unit_price"]) - (L["discount"] or Decimal("0"))
        vm_lines.append(
            LineVM(
                designation=L["designation"],
                description=L["description"],
                quantity=float(L["qty"]),
                unit_price=float(L["unit_price"]),
                tax_rate_display=float(L["tax_rate_pct"]),
                total_ht=float(total_ht),
            )
        )

    vm = QuoteViewModel(
        seller=dto.seller,
        client=dto.client,
        meta=dto.meta,
        lines=vm_lines,
        totals=TotalsVM(
            subtotal=float(totals["subtotal"]),
            tax=float(totals["tax_total"]),
            grand_total=float(totals["grand_total"]),
        ),
        branding=dto.branding or None,  # ✅ Reste compatible, mais sera enrichi par les views
    )
    return vm
