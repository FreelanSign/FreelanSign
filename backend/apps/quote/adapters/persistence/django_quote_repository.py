from __future__ import annotations
from decimal import Decimal
from django.db import transaction
from apps.quote.models import Quote, QuoteLineItem
from apps.quote.application.ports.quote_repository import QuoteRepository

class DjangoQuoteRepository(QuoteRepository):
    """Quote repository using Django ORM."""
    def get(self, quote_id, *, include_lines=True):
        """Get a quote by id."""
        qs = Quote.objects.select_related("client")
        if include_lines:
            qs = qs.prefetch_related("items")
        return qs.get(pk=quote_id)

    def save_header(self, quote: Quote, *, update_totals=False):
        """Save a quote header."""
        if update_totals:
            quote.recalculate_totals(save=True)
        else:
            quote.save(update_fields=[...])  # or quote.save() per your need

    @transaction.atomic
    def replace_lines(self, quote: Quote, items: list[dict]):
        """Replace the lines of a quote."""
        quote.items.all().delete()
        for i, it in enumerate(items):
            QuoteLineItem.objects.create(
                quote=quote,
                description=it["description"][:255],
                qty=it["qty"],
                unit_price=it["unit_price"],
                tax_rate=it["tax_rate_pct"],   # already normalized to %
                discount=it.get("discount", Decimal("0.00")),
                order=i,
                metadata=it.get("metadata", {}),
            )
        quote.recalculate_totals(save=True)

    def add_line_item(self, quote_id: str, *, description: str, qty: Decimal, unit_price: Decimal, tax_rate_pct: Decimal, discount: Decimal, order: int, metadata: dict):
        """Add a line item to a quote."""
        with transaction.atomic():
            quote = Quote.objects.select_for_update().get(pk=quote_id)
            line = QuoteLineItem.objects.create(
                quote=quote,
                description=description[:255],
                qty=qty,
                unit_price=unit_price,
                tax_rate=tax_rate_pct,
                discount=discount,
                order=order,
                metadata=metadata or {},
            )
            quote.recalculate_totals(save=True)
            quote.refresh_from_db()
        return quote, line
