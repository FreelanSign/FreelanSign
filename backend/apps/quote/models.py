# apps/quote/models.py
from __future__ import annotations

import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F, Q, UniqueConstraint, Index
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone


# Reusable decimal options for money-like fields
DECIMAL_KWARGS = dict(max_digits=12, decimal_places=2, default=Decimal("0.00"))

class PaymentTerms(models.Model):
    """
    Payment terms template owned by a user. Helps standardize due dates.
    Example: 'Net 30', 30 days.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_terms",
        help_text="Owner of these payment terms."
    )
    name = models.CharField(max_length=128, help_text="Short label, e.g. 'Net 30'.")
    days = models.PositiveIntegerField(help_text="Number of days to add to issue_date.")
    description = models.TextField(blank=True, help_text="Optional internal description.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quote_payment_terms"
        verbose_name = "Payment terms"
        verbose_name_plural = "Payment terms"
        constraints = [
            # Ensure a user cannot duplicate the same name
            UniqueConstraint(fields=["owner", "name"], name="uq_paymentterms_owner_name"),
        ]
        indexes = [
            Index(fields=["owner", "name"], name="ix_paymentterms_owner_name"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.days}d)"


class Quote(models.Model):
    """
    Commercial quote document. Stores header amounts separately from line items
    to allow integrity checks and faster reads.
    """
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SENT = "SENT", "Sent"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Who owns the quote
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="quotes",
        help_text="Quote owner (user/professional)."
    )

    # Client reference — adapt the dotted path to your Client model
    client = models.ForeignKey(
        "client.Client",  # change to your actual app label if different
        on_delete=models.PROTECT,
        related_name="quotes",
        help_text="Client associated with this quote."
    )

    title = models.CharField(max_length=255)
    reference = models.CharField(
        max_length=64,
        help_text="Human-readable reference unique per owner."
    )
    currency = models.CharField(max_length=3, help_text="ISO currency code, e.g. 'EUR'.")
    language = models.CharField(max_length=8, default="fr", help_text="IETF language tag, e.g. 'fr', 'en'.")

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    issue_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    # Payment terms: either a FK (preferred) or a free text fallback for custom terms.
    payment_terms = models.ForeignKey(
        PaymentTerms,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
        help_text="Optional reference to predefined payment terms."
    )
    payment_terms_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional free-text payment terms if not using a template."
    )

    # Monetary fields (always Decimal)
    subtotal = models.DecimalField(**DECIMAL_KWARGS, help_text="Sum of line pre-tax totals.")
    tax_total = models.DecimalField(**DECIMAL_KWARGS, help_text="Sum of taxes for the quote.")
    discount_total = models.DecimalField(**DECIMAL_KWARGS, help_text="Global discount applied to the quote.")
    total = models.DecimalField(**DECIMAL_KWARGS, help_text="Expected: subtotal + tax_total - discount_total.")

    note = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to="quotes/%Y/%m/", null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "quote_quote"
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"
        constraints = [
            # Uniqueness of reference per owner
            UniqueConstraint(fields=["owner", "reference"], name="uq_quote_owner_reference"),
            # Check that total == subtotal + tax_total - discount_total
            # We use Q(...) with F(...) arithmetic which Django accepts here.
            models.CheckConstraint(
                name="ck_quote_totals_match",
                check=F("total") == Coalesce(F("subtotal"), Decimal("0.00")) + Coalesce(F("tax_total"), Decimal("0.00")) - Coalesce(F("discount_total"), Decimal("0.00")),
            ),
        ]
        indexes = [
            Index(fields=["owner", "reference"], name="ix_quote_owner_reference"),
            Index(fields=["status"], name="ix_quote_status"),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.reference} — {self.title}"

    # ----- Helpers for business integrity -----

    def compute_subtotal(self) -> Decimal:
        """
        Compute subtotal as the sum of line pre-tax totals (qty*unit - discount).
        Tax is excluded by design here to keep amounts consistent with tax_total.
        """
        total = Decimal("0.00")
        for li in self.items.all():
            total += li.pre_tax_total()
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def compute_tax_total(self) -> Decimal:
        """
        Compute taxes by summing each line's tax amount based on its rate.
        """
        taxes = Decimal("0.00")
        for li in self.items.all():
            taxes += li.tax_amount()
        return taxes.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def compute_total(self) -> Decimal:
        """
        Compute grand total = subtotal + tax_total - discount_total.
        """
        return (self.compute_subtotal() + self.compute_tax_total() - self.discount_total)\
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def totals_match(self) -> bool:
        """
        Quick integrity check used by tests to verify stored amounts are coherent.
        """
        return self.total == self.compute_total()

    def recalculate_totals(self, save: bool = True):
        """
        Recalculate subtotal, tax_total and total from line items and persist them.

        - Use precise Decimal arithmetic and round to cents.
        - Use an atomic DB update (QuerySet.update) to avoid triggering recursive signals/saves.
        """
        from django.db import connection  # not required, just for context

        subtotal = self.compute_subtotal()
        tax_total = self.compute_tax_total()
        discount_total = self.discount_total or Decimal("0.00")

        total = (subtotal + tax_total - discount_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # update the instance attributes (so caller has in-memory updated values)
        self.subtotal = subtotal
        self.tax_total = tax_total
        self.total = total

        if save:
            # Use update to avoid triggering save() hooks that might call recalculate_totals again.
            # Also update updated_at manually (auto_now doesn't run on update()).
            from django.utils import timezone
            Quote.objects.filter(pk=self.pk).update(
                subtotal=subtotal,
                tax_total=tax_total,
                total=total,
                updated_at=timezone.now()
            )

    def clean(self):
        """
        Validate that header totals match derived totals.
        Prefer to call recalculate_totals() instead of relying on external user input.
        """
        expected = (self.subtotal or Decimal("0.00")) + (self.tax_total or Decimal("0.00")) - (self.discount_total or Decimal("0.00"))
        expected = expected.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if (self.total or Decimal("0.00")).quantize(Decimal("0.01")) != expected:
            raise ValidationError({"total": f"Total mismatch: expected {expected} but got {self.total}"})

class QuoteLineItem(models.Model):
    """
    Line item belonging to a Quote.
    Stores a metadata JSON field that keeps a reference to the catalog (area_key, prestation_name, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    quote = models.ForeignKey(
        "quote.Quote",
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Owning quote."
    )
    description = models.CharField(max_length=255)
    qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Quantity (can be fractional)."
    )
    unit_price = models.DecimalField(
        **DECIMAL_KWARGS,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Unit price (in EUR). Use Decimal, not float."
    )

    # tax_rate as percentage (0..100). Defaulted when creating the line from the owner/profile.
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))],
        help_text="Tax rate as percentage (e.g. 20.00 for 20%)."
    )

    # per-line absolute discount (in EUR)
    discount = models.DecimalField(
        **DECIMAL_KWARGS,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Line-level discount as absolute amount (EUR)."
    )

    # stored pre-tax total for faster reads (kept in sync in save())
    line_total = models.DecimalField(**DECIMAL_KWARGS, help_text="Pre-tax total; computed on save().")

    order = models.PositiveIntegerField(default=0, help_text="Display order within the quote.")

    # Keep small structured provenance info: area_key, prestation_id, prestation_name, catalog_status...
    metadata = models.JSONField(default=dict, blank=True, help_text="Origin metadata (catalog reference).")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quote_line_item"
        ordering = ["order", "created_at"]
        indexes = [
            Index(fields=["quote", "order"], name="ix_qlitem_quote_order"),
        ]

    # --- computations ---------------------------------------------------------------------------------
    def pre_tax_total(self) -> Decimal:
        """
        Compute pre-tax total = qty * unit_price - discount (never below 0).
        """
        base = (self.qty * self.unit_price) - self.discount
        if base < 0:
            base = Decimal("0.00")
        return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def tax_amount(self) -> Decimal:
        """
        Compute tax amount for this line = pre_tax_total * (tax_rate / 100).
        """
        return (self.pre_tax_total() * (self.tax_rate / Decimal("100")))\
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        """
        Keep the stored pre-tax 'line_total' in sync before saving.
        """
        # update derived field before persisting
        self.line_total = self.pre_tax_total()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.description} ({self.qty} × {self.unit_price})"

class QuoteHistory(models.Model):
    """
    Audit log for significant quote events (create/update/send/status changes).
    """
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        SENT = "sent", "Sent"
        STATUS_CHANGED = "status_changed", "Status changed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="history",
        help_text="Related quote."
    )
    payload_snapshot = models.JSONField(default=dict, blank=True, help_text="Light snapshot for traceability.")
    action = models.CharField(max_length=32, choices=Action.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_actions",
        help_text="User who performed the action, if any."
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "quote_history"
        verbose_name = "Quote history"
        verbose_name_plural = "Quote history"
        indexes = [
            Index(fields=["quote", "timestamp"], name="ix_qhistory_quote_ts"),
            Index(fields=["action"], name="ix_qhistory_action"),
        ]
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.action} on {self.quote.reference} at {self.timestamp:%Y-%m-%d %H:%M}"
