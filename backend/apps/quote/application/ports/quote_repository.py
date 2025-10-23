from __future__ import annotations
from typing import Protocol, Iterable, Any
from decimal import Decimal

class QuoteRepository(Protocol):
    """
    Access to quotes (persistence). The concrete implementations (Django ORM) live in adapters/persistence.
    The DTO/structures returned can be simple objects (e.g. dicts / dataclasses) according to your choice.
    """

    def get(self, *, quote_id, requester_id) -> Any:
        """ Get a quote by id. """
        ...

    def save_header(
        self,
        *,
        quote_id,
        fields: dict,  # example: {"title": "...", "status": "SENT", ...}
    ) -> None:
        """ Save the header of a quote. """
        ...

    def replace_lines(
        self,
        *,
        quote_id,
        lines: Iterable[dict],  # ex: [{"description":..., "qty":D, "unit_price":D, "tax_rate_pct":D, "discount":D, "order":int}, ...]
    ) -> None:
        """ Replace the lines of a quote. """
        ...

    def recalc_totals(self, *, quote_id) -> dict[str, Decimal]:
        """ Recalculate the totals of a quote. """
        ...

    def add_line_item(self, quote_id: str, *, description: str, qty: Decimal, unit_price: Decimal, tax_rate_pct: Decimal,   discount: Decimal, order: int, metadata: dict) -> None:
        """ Add a line item to a quote. """
        ...
