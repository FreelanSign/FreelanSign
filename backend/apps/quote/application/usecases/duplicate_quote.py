from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.quote.application.ports.quote_repository import QuoteRepository


class DuplicateQuote:
    """Duplicate a quote."""

    def __init__(self, repo: QuoteRepository, reference_gen):
        self.repo = repo
        self.reference_gen = reference_gen

    def execute(self, *, quote_id: str, account_id: int, actor):
        """Duplicate a quote."""
        orig = self.repo.get(quote_id, include_lines=True)
        # Phase 5: Use account_id for reference generation
        ref = self.reference_gen.new(account_id)
        # construct header clone
        from apps.quote.models import Quote, QuoteHistory, QuoteLineItem

        new_q = Quote.objects.create(
            account_id=account_id,
            owner=orig.owner,  # Keep for backward compat
            client=orig.client,
            title=f"{orig.title} (copy)",
            reference=ref,
            currency=orig.currency,
            language=orig.language,
            status=Quote.Status.DRAFT,
            issue_date=timezone.now().date(),
            valid_until=orig.valid_until,
            payment_terms=orig.payment_terms,
            payment_terms_text=orig.payment_terms_text,
            note=orig.note,
            metadata=orig.metadata or {},
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=orig.discount_total or Decimal("0.00"),
            total=Decimal("0.00"),
        )
        for li in orig.items.all():
            QuoteLineItem.objects.create(
                quote=new_q,
                description=li.description,
                qty=li.qty,
                unit_price=li.unit_price,
                tax_rate=li.tax_rate,
                discount=li.discount,
                order=li.order,
                metadata=li.metadata or {},
            )
        new_q.recalculate_totals(save=True)
        QuoteHistory.objects.create(
            quote=new_q,
            payload_snapshot={"duplicated_from": str(orig.pk)},
            action=QuoteHistory.Action.CREATED,
            actor=actor,
        )
        return new_q
