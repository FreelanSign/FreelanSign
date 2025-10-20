# apps/quote/application/dto/quote_inputs.py
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class LineItemInputDto:
    """DTO for a line item input.

    Args:
        description: The description of the line item.
        qty: The quantity of the line item.
        unit_price: The unit price of the line item.
        tax_rate: The tax rate of the line item.
        discount: The discount of the line item.
        tax_rate_pct: The tax rate of the line item (as percentage).
    """
    description: str
    qty: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    discount: Decimal | None = None
    tax_rate_pct: Decimal | None = None


@dataclass(frozen=True)
class PreviewPayloadDto:
    """DTO for a preview payload.

    Args:
        seller: The seller of the quote.
        client: The client of the quote.
        meta: The meta data of the quote.
        lines: The line items of the quote.
        branding: The branding of the quote.
    """
    seller: dict
    client: dict
    meta: dict
    lines: list[LineItemInputDto]
    branding: dict | None
    owner_vat_exempt: bool
    owner_default_tax_rate: Decimal
    client_country: str | None
