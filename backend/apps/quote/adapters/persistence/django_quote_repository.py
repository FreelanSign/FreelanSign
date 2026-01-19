# apps/quote/adapters/persistence/django_quote_repository.py
from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from apps.quote.application.errors import QuoteNotFoundError
from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.quote.models import Quote, QuoteLineItem


class DjangoQuoteRepository(QuoteRepository):
    """
    DjangoQuoteRepository – Django ORM implementation of the @QuoteRepository port.

    This adapter encapsulates all persistence logic related to quotes, isolating
    Django-specific operations from the application and domain layers.

    Conforms to Clean Architecture principles:
    - Keeps domain pure by preventing ORM leakage
    - Implements the QuoteRepository interface defined in the application layer
    - Encourages inversion of control and testability via mocking

    All mutation methods are atomic where necessary. Business logic such as
    reference generation or totals computation belongs to the application layer.
    """

    def get(self, quote_id, *, requester_id: str, include_lines=True) -> Quote:
        """Get a quote by id."""
        # REFACTOR (Bertrand - 2025-11-07): Envisager d'ajouter `requester_id` dans QuoteRepository.get()
        # pour vérifier la propriété de la quote avant retour (vérification de sécurité).
        # Attention : nécessite adaptation de toutes les implémentations du repo.

        qs = Quote.objects.select_related("client")
        if include_lines:
            qs = qs.prefetch_related("items")
        try:
            return qs.get(pk=quote_id)
        except Quote.DoesNotExist:
            raise QuoteNotFoundError()

    def create(self, *, account_id: int, fields: dict) -> str:
        """
        Create a new quote header with initial totals set to zero.

        Phase 5: Uses account FK (owner kept for backward compat until Phase 6).
        """
        quote = Quote.objects.create(
            account_id=account_id,
            owner_id=fields.pop("owner_id", None),  # Backward compat (optional)
            **fields,
            subtotal=Decimal(0.00),
            tax_total=Decimal(0.00),
            discount_total=Decimal(0.00),
            total=Decimal(0.00),
        )
        return quote.id

    def save_header(self, *, quote_id, fields: dict):
        """Save a quote header."""
        Quote.objects.filter(pk=quote_id).update(**fields)

    def replace_lines(self, *, quote_id, lines: list[dict]):
        """Replace all line items for a quote by its ID."""
        quote = Quote.objects.get(pk=quote_id)
        quote.items.all().delete()
        for i, it in enumerate(lines):
            QuoteLineItem.objects.create(
                quote=quote,
                description=it["description"][:255],
                details=it.get("details", "") or "",
                qty=it["qty"],
                unit_price=it["unit_price"],
                tax_rate=it.get("tax_rate") or it.get("tax_rate_pct") or Decimal("0.00"),
                discount=it.get("discount", Decimal("0.00")),
                order=i,
                metadata=it.get("metadata", {}),
            )
        quote.recalculate_totals(save=True)

    def add_line_item(
        self,
        quote_id: str,
        *,
        description: str,
        details: str = "",
        qty: Decimal,
        unit_price: Decimal,
        tax_rate_pct: Decimal,
        discount: Decimal,
        order: int,
        metadata: dict,
    ):
        """Add a line item to a quote."""
        with transaction.atomic():
            quote = Quote.objects.select_for_update().get(pk=quote_id)
            line = QuoteLineItem.objects.create(
                quote=quote,
                description=description[:255],
                details=details,
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

    def recalc_totals(self, *, quote_id: str) -> dict:
        """Recalculate and return totals for a quote by ID."""
        quote = Quote.objects.get(pk=quote_id)
        quote.recalculate_totals(save=True)
        quote.refresh_from_db()
        return {
            "subtotal": quote.subtotal,
            "tax_total": quote.tax_total,
            "discount_total": quote.discount_total,
            "total": quote.total,
        }
