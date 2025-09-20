# apps/quote/interface/serializers.py
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, getcontext
from typing import Any, Dict

from django.contrib.auth import get_user_model
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
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


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


class ClientReadSerializer(serializers.ModelSerializer):
    """Small representation of client for read endpoints."""

    class Meta:
        model = Client
        fields = ["id", "name"]


class QuoteCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer that accepts nested items and computes totals server-side.
    Note: 'client' field MUST be present in Meta.fields (fix for the AssertionError).
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

    def validate(self, data):
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

        profile = getattr(owner, "profile", None)
        vat_exempt = bool(getattr(profile, "vat_exempt", False))
        owner_default_tax = getattr(profile, "default_tax_rate", None)
        if owner_default_tax is not None:
            owner_default_tax = Decimal(str(owner_default_tax))
        else:
            owner_default_tax = GLOBAL_DEFAULT_TAX_RATE

        client_obj = data.get("client")
        client_country = None
        if client_obj is not None:
            client_country = getattr(client_obj, "country", None)
            if client_country in (None, ""):
                try:
                    meta = getattr(client_obj, "metadata", None)
                    if isinstance(meta, dict):
                        client_country = meta.get("country") or meta.get("country_code") or meta.get("billing_country")
                except Exception:
                    client_country = None
        if client_country is not None:
            client_country = str(client_country).upper()

        item_tax_rates = []
        for item in items:
            tax_field = item.get("tax_rate", None)
            if tax_field is None:
                assumed = ZERO if vat_exempt else owner_default_tax
                item_tax_rates.append(assumed)
            else:
                item_tax_rates.append(Decimal(str(tax_field)))

        if vat_exempt:
            non_zero = [t for t in item_tax_rates if quantize_money(t) != ZERO]
            if non_zero:
                raise ValidationError({"items": "Owner is VAT-exempt; line tax rates must be 0."})

        if client_country and client_country in {"FR", "FRA", "FRANCE"} and not vat_exempt:
            zero_rates = [i for i, t in enumerate(item_tax_rates) if quantize_money(t) == ZERO]
            if zero_rates:
                raise ValidationError(
                    {"items": f"VAT missing for French client on lines: {zero_rates}. Owner must apply VAT or be VAT-exempt."}
                )

        return data

    def _derive_tax_rate_for_item(self, owner, item_data: Dict[str, Any]) -> Decimal:
        profile = getattr(owner, "profile", None)
        vat_exempt = bool(getattr(profile, "vat_exempt", False))
        if vat_exempt:
            return ZERO
        if "tax_rate" in item_data and item_data["tax_rate"] is not None:
            return Decimal(str(item_data["tax_rate"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        owner_default = getattr(profile, "default_tax_rate", None)
        if owner_default is not None:
            return Decimal(str(owner_default)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return GLOBAL_DEFAULT_TAX_RATE

    def _compute_line_values(self, item_data: Dict[str, Any], tax_rate: Decimal) -> Dict[str, Decimal]:
        qty = Decimal(str(item_data.get("qty", "0")))
        unit_price = Decimal(str(item_data.get("unit_price", "0")))
        discount = Decimal(str(item_data.get("discount", "0")))

        pre_tax = qty * unit_price - discount
        if pre_tax < ZERO:
            pre_tax = ZERO
        pre_tax = quantize_money(pre_tax)
        tax_amount = quantize_money(pre_tax * (tax_rate / Decimal("100.00")))
        return {"pre_tax_total": pre_tax, "tax_amount": tax_amount}

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        request = self.context["request"]
        owner = request.user

        quote = Quote.objects.create(owner=owner, **validated_data, subtotal=ZERO, tax_total=ZERO, total=ZERO)

        subtotal = ZERO
        tax_total = ZERO
        for order, item in enumerate(items_data):
            tax_rate = self._derive_tax_rate_for_item(owner, item)
            vals = self._compute_line_values(item, tax_rate)
            if Decimal(str(item.get("qty", "0"))) <= ZERO:
                raise ValidationError({"items": f"Line {order}: qty must be > 0."})
            if Decimal(str(item.get("unit_price", "0"))) < ZERO:
                raise ValidationError({"items": f"Line {order}: unit_price must be >= 0."})
            if Decimal(str(item.get("discount", "0"))) < ZERO:
                raise ValidationError({"items": f"Line {order}: discount must be >= 0."})

            line = QuoteLineItem.objects.create(
                quote=quote,
                description=item.get("description", "")[:255],
                qty=Decimal(str(item.get("qty"))),
                unit_price=quantize_money(Decimal(str(item.get("unit_price")))),
                tax_rate=tax_rate,
                discount=quantize_money(Decimal(str(item.get("discount", "0")))),
                order=order,
                metadata=item.get("metadata", {}) or {},
            )
            subtotal += line.pre_tax_total()
            tax_total += line.tax_amount()

        discount_total = validated_data.get("discount_total", ZERO) or ZERO
        discount_total = quantize_money(Decimal(str(discount_total)))

        subtotal = quantize_money(subtotal)
        tax_total = quantize_money(tax_total)
        total = quantize_money(subtotal + tax_total - discount_total)

        Quote.objects.filter(pk=quote.pk).update(
            subtotal=subtotal, tax_total=tax_total, discount_total=discount_total, total=total
        )
        quote.refresh_from_db()
        return quote

    @transaction.atomic
    def update(self, instance: Quote, validated_data):
        items_data = validated_data.pop("items", [])
        request = self.context["request"]
        owner = request.user

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        instance.items.all().delete()

        subtotal = ZERO
        tax_total = ZERO
        for order, item in enumerate(items_data):
            tax_rate = self._derive_tax_rate_for_item(owner, item)
            line = QuoteLineItem.objects.create(
                quote=instance,
                description=item.get("description", "")[:255],
                qty=Decimal(str(item.get("qty"))),
                unit_price=quantize_money(Decimal(str(item.get("unit_price")))),
                tax_rate=tax_rate,
                discount=quantize_money(Decimal(str(item.get("discount", "0")))),
                order=order,
                metadata=item.get("metadata", {}) or {},
            )
            subtotal += line.pre_tax_total()
            tax_total += line.tax_amount()

        discount_total = getattr(instance, "discount_total", ZERO) or ZERO
        discount_total = quantize_money(Decimal(str(discount_total)))

        subtotal = quantize_money(subtotal)
        tax_total = quantize_money(tax_total)
        total = quantize_money(subtotal + tax_total - discount_total)

        Quote.objects.filter(pk=instance.pk).update(
            subtotal=subtotal, tax_total=tax_total, discount_total=discount_total, total=total
        )
        instance.refresh_from_db()
        return instance


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
