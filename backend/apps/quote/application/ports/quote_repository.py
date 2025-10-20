from __future__ import annotations
from typing import Protocol, Iterable, Any
from decimal import Decimal

class QuoteRepository(Protocol):
    """
    Access to quotes (persistence). The concrete implementations (Django ORM) live in adapters/persistence.
    The DTO/structures returned can be simple objects (e.g. dicts / dataclasses) according to your choice.
    """

    def get(self, *, quote_id, requester_id) -> Any: ...
    def save_header(
        self,
        *,
        quote_id,
        fields: dict,  # example: {"title": "...", "status": "SENT", ...}
    ) -> None: ...
    def replace_lines(
        self,
        *,
        quote_id,
        lines: Iterable[dict],  # ex: [{"description":..., "qty":D, "unit_price":D, "tax_rate_pct":D, "discount":D, "order":int}, ...]
    ) -> None: ...
    def recalc_totals(self, *, quote_id) -> dict[str, Decimal]: ...
