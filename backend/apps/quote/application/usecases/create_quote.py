import logging
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.client.models import Client
from apps.core.utils.money import cents_to_euros, euros_to_cents
from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.quote.application.ports.reference_gen import QuoteReferenceGeneratorPort
from apps.quote.models import Quote, QuoteLineItem

logger = logging.getLogger(__name__)

ZERO = Decimal("0.00")


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


class CreateQuoteUseCase:
    """
    Application use case for creating a new quote.

    Responsibilities:
    - Validate client ownership if a patch is provided
    - Generate reference using the reference generator
    - Delegate creation to the quote repository
    - Compute and update totals (subtotal, tax, discount, total)

    This use case remains agnostic of the persistence layer (via QuoteRepository).
    """

    def __init__(self, *, ref_generator: QuoteReferenceGeneratorPort, quote_repository: QuoteRepository):
        self.ref_generator = ref_generator
        self.quote_repository = quote_repository

    @transaction.atomic
    def execute(
        self,
        *,
        account_id: int,  # Phase 5: account FK
        requester_id: int,  # For permission checks
        validated_data: dict,
        client_patch: Optional[Dict[str, Any]] = None,
    ) -> Quote:
        items = validated_data.pop("items", [])
        issue_date: date = validated_data.get("issue_date") or timezone.localdate()
        client: Client = validated_data["client"]

        if client_patch:
            logger.info("client.update.before_create", extra={"client_id": str(client.id)})
            self._apply_client_update(client, client_patch, requester_id=requester_id)

        validated_data.pop("reference", None)
        raw_discount_total = validated_data.pop("discount_total", ZERO)
        # Phase 5: Use account_id for reference generation
        reference = self.ref_generator.next_reference(owner_id=account_id, when=issue_date)
        validated_data["reference"] = reference

        # Phase 5: Create with account_id
        # Backward compat: Ensure owner_id is set (requester is owner)
        validated_data["owner_id"] = requester_id
        quote_id = self.quote_repository.create(account_id=account_id, fields=validated_data)
        logger.info("quote.created", extra={"quote_id": str(quote_id)})
        quote = self.quote_repository.get(quote_id=quote_id, requester_id=requester_id)
        logger.debug("quote.loaded.after_creation", extra={"quote_id": quote_id})

        subtotal, tax_total = self._create_items_and_compute_totals(quote, items)
        discount_total = quantize_money(Decimal(str(raw_discount_total or ZERO)))
        total = quantize_money(subtotal + tax_total - discount_total)

        Quote.objects.filter(pk=quote.pk).update(
            subtotal=subtotal,
            tax_total=tax_total,
            discount_total=discount_total,
            total=total,
        )
        quote.refresh_from_db()

        logger.info(
            "quote.create.finish",
            extra={
                "quote_id": str(quote.id),
                "subtotal": str(quote.subtotal),
                "tax_total": str(quote.tax_total),
                "discount_total": str(quote.discount_total),
                "total": str(quote.total),
            },
        )

        return quote

    def _apply_client_update(self, client: Client, patch: dict, *, requester_id: int) -> None:
        # TODO Phase 5.2: Update when Client has account FK
        if client.owner_id != requester_id:
            logger.warning("client.update.forbidden", extra={"client_id": str(client.id), "requester_id": requester_id})
            raise ValidationError({"client": "You do not own this client."})

        allowed_fields = {"name", "email", "phone", "address", "vat_number", "metadata"}
        changed = {}

        for field, value in patch.items():
            if field in allowed_fields:
                old = getattr(client, field, None)
                new = value if value is not None else ""
                if old != new:
                    setattr(client, field, new)
                    changed[field] = (old, new)

        if changed:
            client.save(update_fields=list(changed.keys()))
            for field, (old, new) in changed.items():
                logger.info(
                    "client.field.updated",
                    extra={
                        "client_id": str(client.id),
                        "field": field,
                        "old": str(old),
                        "new": str(new),
                    },
                )
        else:
            logger.debug("client.no_changes", extra={"client_id": str(client.id)})

    def _create_items_and_compute_totals(self, quote: Quote, items: list[dict]) -> tuple[Decimal, Decimal]:
        subtotal = ZERO
        tax_total = ZERO

        for item_data in items:
            item = QuoteLineItem.objects.create(quote=quote, **item_data)
            subtotal += item.pre_tax_total()
            tax_total += item.tax_amount()

        return quantize_money(subtotal), quantize_money(tax_total)
