# apps/quote/application/dto/quote_viewmodels.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LineVM:
    """ViewModel for a line item.

    Args:
        designation: The designation of the line item.
        description: The description of the line item.
        quantity: The quantity of the line item.
        unit_price: The unit price of the line item.
        tax_rate_display: The tax rate of the line item (as percentage).
        total_ht: The total HT of the line item.
    """

    designation: str
    description: str | None
    quantity: float
    unit_price: float
    tax_rate_display: float
    total_ht: float


@dataclass(frozen=True)
class TotalsVM:
    """ViewModel for the totals.

    Args:
        subtotal: The subtotal of the quote.
        tax: The tax total of the quote.
        grand_total: The grand total of the quote.
    """

    subtotal: float
    tax: float
    grand_total: float


@dataclass(frozen=True)
class QuoteViewModel:
    """ViewModel for a quote.

    Args:
        seller: The seller of the quote.
        client: The client of the quote.
        meta: The meta data of the quote.
        lines: The line items of the quote.
        totals: The totals of the quote.
        branding: The branding of the quote.
    """

    seller: dict
    client: dict
    meta: dict
    lines: list[LineVM]
    totals: TotalsVM
    branding: dict | None
