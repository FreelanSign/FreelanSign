# apps/quote/interface/serializers.py
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, getcontext
from typing import Any, Dict, Iterable, List, Tuple

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.client.models import Client
from apps.quote.models import Quote, QuoteLineItem

getcontext().prec = 28

CENT = Decimal("0.01")
ZERO = Decimal("0.00")
GLOBAL_DEFAULT_TAX_RATE = Decimal("20.00")


def quantize_money(value: Decimal) -> Decimal:
    """Quantize monetary Decimal to 2 decimals using ROUND_HALF_UP."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


# ----------------------------
# Line item serializer
# ----------------------------
class QuoteLineItemSerializer(serializers.ModelSerializer):
    pre_tax_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = QuoteLineItem
        fields = [
            "id",
            "description",
            "qty",
            "unit_price",
            "tax_rate",
            "discount",
            "pre_tax_total",
            "tax_amount",
            "order",
            "metadata",
        ]
        read_only_fields = ["id", "pre_tax_total", "tax_amount"]

    # Field-level validators
    def validate_qty(self, value: Decimal) -> Decimal:
        if value <= ZERO:
            raise ValidationError("Quantity must be greater than 0.")
        return quantize_money(value)

    def validate_unit_price(self, value: Decimal) -> Decimal:
        if value < ZERO:
            raise ValidationError("Unit price must be >= 0.")
        return quantize_money(value)

    def validate_discount(self, value: Decimal) -> Decimal:
        if value < ZERO:
            raise ValidationError("Discount must be >= 0.")
        return quantize_money(value)

    def validate_tax_rate(self, value: Decimal) -> Decimal:
        if value is None:
            return value
        if value < ZERO or value > Decimal("100.00"):
            raise ValidationError("Tax rate must be between 0 and 100 (percentage).")
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def to_representation(self, instance: QuoteLineItem) -> Dict[str, Any]:
        rep = super().to_representation(instance)
        rep["pre_tax_total"] = str(quantize_money(instance.pre_tax_total()))
        rep["tax_amount"] = str(quantize_money(instance.tax_amount()))
        return rep


# ----------------------------
# Small client read serializer
# ----------------------------
class ClientReadSerializer(serializers.ModelSerializer):
    """Small representation of client for read endpoints."""

    class Meta:
        model = Client
        fields = ["id", "name"]


# ----------------------------
# Helpers used by QuoteCreateUpdateSerializer
# ----------------------------
def _get_client_country(client_obj) -> str | None:
    """
    Determine client country string in normalized uppercase form.
    Accepts direct attribute or fallback to client.metadata dictionary keys.
    """
    if client_obj is None:
        return None
    country = getattr(client_obj, "country", None)
    if country:
        return str(country).upper()
    # fallback to metadata if present
    meta = getattr(client_obj, "metadata", None)
    if isinstance(meta, dict):
        for key in ("country", "country_code", "billing_country"):
            val = meta.get(key)
            if val:
                return str(val).upper()
    return None


def _owner_vat_config(owner) -> Tuple[bool, Decimal]:
    """
    Return tuple (vat_exempt: bool, owner_default_tax: Decimal).
    Defaults to (False, GLOBAL_DEFAULT_TAX_RATE) if not present.
    """
    profile = getattr(owner, "profile", None)
    vat_exempt = bool(getattr(profile, "vat_exempt", False))
    owner_default = getattr(profile, "default_tax_rate", None)
    if owner_default is not None:
        owner_default = Decimal(str(owner_default)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        owner_default = GLOBAL_DEFAULT_TAX_RATE
    return vat_exempt, owner_default


def _collect_item_tax_rates(items: Iterable[dict], vat_exempt: bool, owner_default_tax: Decimal) -> List[Decimal]:
    """
    Return list of tax rates (Decimal) for each provided item, using owner defaults when missing.
    """
    rates: List[Decimal] = []
    for item in items:
        tax = item.get("tax_rate", None)
        if tax is None:
            assumed = ZERO if vat_exempt else owner_default_tax
            rates.append(assumed)
        else:
            rates.append(Decimal(str(tax)))
    return rates


def _validate_item_basics(item: dict, order: int) -> None:
    """
    Basic per-item validation for qty, unit_price and discount; raises ValidationError with helpful message.
    """
    qty = Decimal(str(item.get("qty", "0")))
    if qty <= ZERO:
        raise ValidationError({"items": f"Line {order}: qty must be > 0."})
    unit_price = Decimal(str(item.get("unit_price", "0")))
    if unit_price < ZERO:
        raise ValidationError({"items": f"Line {order}: unit_price must be >= 0."})
    discount = Decimal(str(item.get("discount", "0")))
    if discount < ZERO:
        raise ValidationError({"items": f"Line {order}: discount must be >= 0."})


def _create_and_accumulate_line(quote: Quote, item: dict, order: int, owner, tax_rate: Decimal) -> Tuple[Decimal, Decimal]:
    """
    Create a QuoteLineItem for the quote and return (pre_tax_total, tax_amount).
    This encapsulates model creation and returns computed values for totals accumulation.
    """
    # create persisted line item; unit_price assumed in EUR Decimal-like string/number
    line = QuoteLineItem.objects.create(
        quote=quote,
        description=(item.get("description", "") or "")[:255],
        qty=Decimal(str(item.get("qty"))),
        unit_price=quantize_money(Decimal(str(item.get("unit_price")))),
        tax_rate=tax_rate,
        discount=quantize_money(Decimal(str(item.get("discount", "0")))),
        order=order,
        metadata=item.get("metadata", {}) or {},
    )
    # model ensures line.line_total saved in save()
    return quantize_money(line.pre_tax_total()), quantize_money(line.tax_amount())


def _create_items_and_compute_totals(quote: Quote, items: List[dict], owner) -> Tuple[Decimal, Decimal]:
    """
    Create line items for a quote and compute subtotal and tax_total.
    Returns (subtotal, tax_total).
    """
    vat_exempt, owner_default = _owner_vat_config(owner)
    subtotal = ZERO
    tax_total = ZERO

    for order, item in enumerate(items):
        _validate_item_basics(item, order)
        # derive tax_rate
        if vat_exempt:
            tax_rate = ZERO
        else:
            if "tax_rate" in item and item.get("tax_rate") is not None:
                tax_rate = Decimal(str(item.get("tax_rate"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                tax_rate = owner_default
        pt, ta = _create_and_accumulate_line(quote, item, order, owner, tax_rate)
        subtotal += pt
        tax_total += ta

    return quantize_money(subtotal), quantize_money(tax_total)


# ----------------------------
# Quote write serializer (create/update)
# ----------------------------
class QuoteCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer that accepts nested items and computes totals server-side.
    """

    items = QuoteLineItemSerializer(many=True)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())

    class Meta:
        model = Quote
        fields = [
            "id",
            "title",
            "reference",
            "currency",
            "language",
            "status",
            "issue_date",
            "valid_until",
            "payment_terms",
            "payment_terms_text",
            "note",
            "metadata",
            "client",
            "items",
        ]
        read_only_fields = ["id"]

    def validate(self, data: dict) -> dict:
        """
        Global validations:
         - at least 1 item
         - valid_until >= issue_date
         - VAT rules based on owner profile and client country
        """
        items = data.get("items") or []
        if len(items) < 1:
            raise ValidationError({"items": "A quote must contain at least one line item."})

        issue_date = data.get("issue_date")
        valid_until = data.get("valid_until")
        if issue_date and valid_until and valid_until < issue_date:
            raise ValidationError({"valid_until": "valid_until must be on or after issue_date."})

        request = self.context.get("request")
        if request is None or not getattr(request, "user", None):
            raise ValidationError("Authenticated request is required to create a quote (owner).")
        owner = request.user

        vat_exempt, owner_default_tax = _owner_vat_config(owner)
        client_country = _get_client_country(data.get("client"))

        # collect assumed tax values for each item
        item_tax_rates = _collect_item_tax_rates(items, vat_exempt, owner_default_tax)

        # Owner VAT exempt cannot have non-zero taxes
        if vat_exempt:
            non_zero = [t for t in item_tax_rates if quantize_money(t) != ZERO]
            if non_zero:
                raise ValidationError({"items": "Owner is VAT-exempt; line tax rates must be 0."})

        # If client is FR and owner not vat_exempt -> tax_rate must not be zero for any line
        if client_country and client_country in {"FR", "FRA", "FRANCE"} and not vat_exempt:
            zero_rates_idx = [i for i, t in enumerate(item_tax_rates) if quantize_money(t) == ZERO]
            if zero_rates_idx:
                raise ValidationError(
                    {
                        "items": f"VAT missing for French client on lines: {zero_rates_idx}. Owner must apply VAT or be VAT-exempt."
                    }
                )

        return data

    @transaction.atomic
    def create(self, validated_data: dict) -> Quote:
        items = validated_data.pop("items", [])
        request = self.context["request"]
        owner = request.user

        # create header with zeroed totals to be persisted later
        quote = Quote.objects.create(owner=owner, **validated_data, subtotal=ZERO, tax_total=ZERO, total=ZERO)

        subtotal, tax_total = _create_items_and_compute_totals(quote, items, owner)

        discount_total = validated_data.get("discount_total", ZERO) or ZERO
        discount_total = quantize_money(Decimal(str(discount_total)))

        total = quantize_money(subtotal + tax_total - discount_total)

        Quote.objects.filter(pk=quote.pk).update(
            subtotal=subtotal, tax_total=tax_total, discount_total=discount_total, total=total
        )
        quote.refresh_from_db()
        return quote

    @transaction.atomic
    def update(self, instance: Quote, validated_data: dict) -> Quote:
        items = validated_data.pop("items", [])
        request = self.context["request"]
        owner = request.user

        # apply header updates (not totals)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # remove existing items and recreate
        instance.items.all().delete()
        subtotal, tax_total = _create_items_and_compute_totals(instance, items, owner)

        discount_total = getattr(instance, "discount_total", ZERO) or ZERO
        discount_total = quantize_money(Decimal(str(discount_total)))

        total = quantize_money(subtotal + tax_total - discount_total)

        Quote.objects.filter(pk=instance.pk).update(
            subtotal=subtotal, tax_total=tax_total, discount_total=discount_total, total=total
        )
        instance.refresh_from_db()
        return instance


# ----------------------------
# Quote read serializer
# ----------------------------
class QuoteSerializer(serializers.ModelSerializer):
    items = QuoteLineItemSerializer(many=True, read_only=True)
    client = ClientReadSerializer(read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = [
            "id",
            "reference",
            "title",
            "currency",
            "language",
            "status",
            "issue_date",
            "valid_until",
            "payment_terms",
            "payment_terms_text",
            "client",
            "subtotal",
            "tax_total",
            "discount_total",
            "total",
            "note",
            "metadata",
            "created_at",
            "updated_at",
            "sent_at",
            "accepted_at",
            "items",
            "pdf_url",
        ]
        read_only_fields = fields

    def get_pdf_url(self, obj: Quote) -> str:
        if obj.pdf_file:
            try:
                return obj.pdf_file.url
            except Exception:
                return ""
        return ""
