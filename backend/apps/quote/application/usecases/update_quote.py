# backend/apps/quote/application/usecases/update_quote.py
import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.client.models import Client
from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.quote.models import Quote

logger = logging.getLogger(__name__)

ZERO = Decimal("0.00")


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


class UpdateQuoteUseCase:
    """
    Application use case for updating an existing quote.

    Responsibilities:
    - Optionally reassign client and apply a client patch
    - Update header fields
    - Replace or preserve line items depending on input
    - Recalculate totals (subtotal, tax, discount, total)
    - Ensure all operations run atomically
    """

    def __init__(self, *, quote_repo: QuoteRepository):
        self.quote_repo = quote_repo

    @transaction.atomic
    def execute(
        self,
        *,
        quote: Quote,
        requester_id: int,  # Phase 5
        validated_data: dict,
        client_patch: Optional[Dict[str, Any]] = None,
        items: Optional[list[dict]] = None,
        items_field_provided: bool = False,
    ) -> Quote:
        quote_id = quote.id

        # --- Client Reassignment ---
        new_client: Optional[Client] = validated_data.get("client")
        if new_client and new_client != quote.client:
            # TODO Phase 5.2: Update when Client has account FK
            if new_client.owner_id != requester_id:
                logger.warning(
                    "quote.update.client.forbidden",
                    extra={
                        "quote_id": str(quote_id),
                        "new_client_id": str(new_client.id),
                        "requester_id": requester_id,
                    },
                )
                raise ValidationError({"client": "You do not own this client."})
            logger.info(
                "quote.update.client.reassigned",
                extra={
                    "quote_id": str(quote_id),
                    "old_client_id": str(quote.client.id),
                    "new_client_id": str(new_client.id),
                },
            )
            quote.client = new_client

        # --- Client patch ---
        if client_patch:
            self._apply_client_patch(quote.client, client_patch, requester_id=requester_id)

        # --- Header fields update ---
        update_fields = {k: v for k, v in validated_data.items() if k not in {"client", "reference", "items"}}
        self.quote_repo.save_header(
            quote_id=quote_id,
            fields=update_fields,
        )

        # --- Line items update ---
        if items_field_provided:
            logger.debug(
                "quote.update.preserve_items",
                extra={
                    "quote_id": str(quote_id),
                    "items_count": len(items) if items else 0,
                },
            )
            self.quote_repo.replace_lines(quote_id=quote_id, lines=items or [])
        else:
            logger.debug("quote.update.preserve_items", extra={"quote_id": str(quote_id)})

        # --- Totals ---
        totals = self.quote_repo.recalc_totals(quote_id=quote_id)
        discount_total = quantize_money(Decimal(str(getattr(quote, "discount_total", ZERO) or ZERO)))
        total = quantize_money(totals["subtotal"] + totals["tax_total"] - discount_total)

        self.quote_repo.save_header(
            quote_id=quote_id,
            fields={
                "subtotal": totals["subtotal"],
                "tax_total": totals["tax_total"],
                "discount_total": discount_total,
                "total": total,
            },
        )

        updated = self.quote_repo.get(quote_id=quote_id, requester_id=requester_id)
        logger.info(
            "quote.update.finish",
            extra={
                "quote_id": str(updated.id),
                "subtotal": str(updated.subtotal),
                "tax_total": str(updated.tax_total),
                "discount_total": str(updated.discount_total),
                "total": str(updated.total),
                "items_field_provided": items_field_provided,
            },
        )
        return updated

    def _apply_client_patch(self, client: Client, patch: dict, *, requester_id: int) -> None:
        # TODO Phase 5.2: Update when Client has account FK
        if client.owner_id != requester_id:
            logger.warning(
                "client.update.forbidden",
                extra={
                    "client_id": str(client.id),
                    "requester_id": requester_id,
                },
            )
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
