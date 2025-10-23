# apps/quote/interface/serializers.py
from __future__ import annotations

import logging
from decimal import ROUND_HALF_UP, Decimal, getcontext
from re import L
from typing import Any, Dict, Iterable, List, Optional, Tuple

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.client.interface.serializers import ClientReadSerializer
from apps.client.models import Client
from apps.core.logging import get_logger
from apps.quote.domain.policies.tax_policy import (
    TaxPolicyError,
    effective_rate_for_line,
    normalize_rate_percent,
    validate_client_vat_rule,
)
from apps.quote.models import Quote, QuoteLineItem

getcontext().prec = 28

CENT = Decimal("0.01")
ZERO = Decimal("0.00")
GLOBAL_DEFAULT_TAX_RATE = Decimal("20.00")


# --------------------------------------------------------------------------------------
# Utils
# --------------------------------------------------------------------------------------
def _qlog(serializer: serializers.Serializer, level: int, msg: str, **kwargs):
    """
    Helper log: récupère le logger contextualisé depuis request (si présent),
    sinon fallback sur logging.getLogger(__name__).
    """
    request = serializer.context.get("request") if hasattr(serializer, "context") else None
    logger = get_logger(__name__, request) if request is not None else logging.getLogger(__name__)
    logger.log(level, msg, extra=kwargs)


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


# --------------------------------------------------------------------------------------
# Line item serializer
# --------------------------------------------------------------------------------------
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
        """Validate the tax rate as a percentage (0..100).

        Args:
            value: The tax rate to validate (as percentage).

        Returns:
            The validated tax rate (as percentage).

        Raises:
            ValidationError: If the tax rate is not between 0 and 100 (percentage).
        """
        if value is None:
            return value
        try:
            return normalize_rate_percent(value)
        except TaxPolicyError as e:
            raise ValidationError(str(e))

    def to_representation(self, instance: QuoteLineItem) -> Dict[str, Any]:
        rep = super().to_representation(instance)
        rep["pre_tax_total"] = str(quantize_money(instance.pre_tax_total()))
        rep["tax_amount"] = str(quantize_money(instance.tax_amount()))
        return rep


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _get_client_country(client_obj) -> str | None:
    if client_obj is None:
        return None
    country = getattr(client_obj, "country", None)
    if country:
        return str(country).upper()
    meta = getattr(client_obj, "metadata", None)
    if isinstance(meta, dict):
        for key in ("country", "country_code", "billing_country"):
            val = meta.get(key)
            if val:
                return str(val).upper()
    return None


def _owner_vat_config(owner) -> Tuple[bool, Decimal]:
    profile = getattr(owner, "profile", None)
    vat_exempt = bool(getattr(profile, "vat_exempt", False))
    owner_default = getattr(profile, "default_tax_rate", None)
    if owner_default is not None:
        owner_default = Decimal(str(owner_default)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        owner_default = GLOBAL_DEFAULT_TAX_RATE
    return vat_exempt, owner_default


def _collect_item_tax_rates(items: Iterable[dict], vat_exempt: bool, owner_default_tax: Decimal) -> List[Decimal]:
    """Collect the tax rates for the items.

    Args:
        items: The items to collect the tax rates for.
        vat_exempt: Whether the owner is VAT-exempt.
        owner_default_tax: The default tax rate for the owner.

    Returns:
        The tax rates for the items.
    """
    rates: List[Decimal] = []
    for item in items:
        raw = item.get("tax_rate", None)
        raw_dec = Decimal(str(raw)) if raw is not None else None
        eff = effective_rate_for_line(raw_dec, owner_vat_exempt=vat_exempt, owner_default_rate_pct=owner_default_tax)
        rates.append(eff)
    return rates


def _validate_item_basics(item: dict, order: int) -> None:
    qty = Decimal(str(item.get("qty", "0")))
    if qty <= ZERO:
        raise ValidationError({"items": f"Line {order}: qty must be > 0."})
    unit_price = Decimal(str(item.get("unit_price", "0")))
    if unit_price < ZERO:
        raise ValidationError({"items": f"Line {order}: unit_price must be >= 0."})
    discount = Decimal(str(item.get("discount", "0")))
    if discount < ZERO:
        raise ValidationError({"items": f"Line {order}: discount must be >= 0."})


def _create_and_accumulate_line(
    serializer: serializers.Serializer, quote: Quote, item: dict, order: int, owner, tax_rate: Decimal
) -> Tuple[Decimal, Decimal]:
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
    pt = quantize_money(line.pre_tax_total())
    ta = quantize_money(line.tax_amount())
    _qlog(
        serializer,
        logging.DEBUG,
        "quote.items.create",
        quote_id=str(getattr(quote, "id", None)),
        line_id=str(getattr(line, "id", None)),
        order=order,
        qty=str(line.qty),
        unit_price=str(line.unit_price),
        tax_rate=str(line.tax_rate),
        pre_tax_total=str(pt),
        tax_amount=str(ta),
    )
    return pt, ta


def _create_items_and_compute_totals(
    serializer: serializers.Serializer, quote: Quote, items: List[dict], owner
) -> Tuple[Decimal, Decimal]:
    vat_exempt, owner_default = _owner_vat_config(owner)
    subtotal = ZERO
    tax_total = ZERO

    _qlog(
        serializer,
        logging.DEBUG,
        "quote.items.start",
        quote_id=str(getattr(quote, "id", None)),
        count=len(items),
        vat_exempt=vat_exempt,
        owner_default_rate_pct=str(owner_default),
    )

    for order, item in enumerate(items):
        _validate_item_basics(item, order)
        raw = item.get("tax_rate", None)
        raw_dec = Decimal(str(raw)) if raw is not None else None
        tax_rate = effective_rate_for_line(raw_dec, owner_vat_exempt=vat_exempt, owner_default_rate_pct=owner_default)
        pt, ta = _create_and_accumulate_line(serializer, quote, item, order, owner, tax_rate)
        subtotal += pt
        tax_total += ta

    subtotal = quantize_money(subtotal)
    tax_total = quantize_money(tax_total)

    _qlog(
        serializer,
        logging.INFO,
        "quote.items.finish",
        quote_id=str(getattr(quote, "id", None)),
        subtotal=str(subtotal),
        tax_total=str(tax_total),
        total=str(quantize_money(subtotal + tax_total)),
    )

    return subtotal, tax_total


# --------------------------------------------------------------------------------------
# Write serializer
# --------------------------------------------------------------------------------------
class QuoteCreateUpdateSerializer(serializers.ModelSerializer):
    items = QuoteLineItemSerializer(many=True)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    client_update = serializers.DictField(required=False, write_only=True)

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
            "client_update",
            "items",
        ]
        read_only_fields = ["id"]

    def validate(self, data: dict) -> dict:
        """Validate the quote data.

        Args:
            data: The quote data to validate.

        Returns:
            The validated quote data.

        Raises:
            ValidationError: If the quote data is invalid.
        """
        items = data.get("items", None)
        if not self.partial:
            if not items or len(items) < 1:
                raise ValidationError({"items": "A quote must contain at least one line item."})
        else:
            if items is not None and len(items) < 1:
                raise ValidationError({"items": "When provided, 'items' must contain at least one line item."})

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
        item_tax_rates = _collect_item_tax_rates(items, vat_exempt, owner_default_tax)

        _qlog(
            self,
            logging.DEBUG,
            "quote.validate",
            owner_id=getattr(owner, "id", None),
            vat_exempt=vat_exempt,
            client_country=client_country,
            item_count=len(items),
            has_client_update=bool(self.initial_data.get("client_update")),
        )

        try:
            validate_client_vat_rule(client_country, vat_exempt, item_tax_rates)
        except TaxPolicyError as e:
            raise ValidationError({"items": str(e)})

        return data

    def _apply_client_update(self, client_obj: Client, patch: dict, *, requester) -> Client:
        if getattr(client_obj, "owner_id", None) != getattr(requester, "id", None):
            _qlog(
                self,
                logging.WARNING,
                "client.update.forbidden",
                client_id=str(getattr(client_obj, "id", None)),
                requester_id=getattr(requester, "id", None),
            )
            raise ValidationError({"client": "You do not own this client."})

        allowed_fields = {"name", "email", "phone", "address", "vat_number", "metadata"}
        changed: Dict[str, Tuple[Any, Any]] = {}

        for k, v in patch.items():
            if k in allowed_fields:
                old = getattr(client_obj, k, None)
                new = v if v is not None else ""
                if old != new:
                    changed[k] = (old, new)
                    setattr(client_obj, k, new)

        if changed:
            client_obj.save(update_fields=[f for f in allowed_fields if hasattr(client_obj, f)])
            # logs détaillés champ par champ
            for field, (old, new) in changed.items():
                # Exemple demandé : "Client ... email updated from .. to .."
                _qlog(
                    self,
                    logging.INFO,
                    "client.field.updated",
                    client_id=str(getattr(client_obj, "id", None)),
                    field=field,
                    old=str(old),
                    new=str(new),
                )
        else:
            _qlog(self, logging.DEBUG, "client.no_changes", client_id=str(getattr(client_obj, "id", None)))

        return client_obj

    @transaction.atomic
    def create(self, validated_data: dict) -> Quote:
        items = validated_data.pop("items", [])
        request = self.context["request"]
        owner = request.user

        client_patch = self.initial_data.get("client_update", None)  # ✅ fix typo
        client_obj: Optional[Client] = validated_data.get("client")

        if client_patch and client_obj:
            _qlog(self, logging.INFO, "client.update.before_create", client_id=str(getattr(client_obj, "id", None)))
            self._apply_client_update(client_obj, client_patch, requester=owner)

        _qlog(
            self,
            logging.INFO,
            "quote.create.start",
            owner_id=getattr(owner, "id", None),
            client_id=str(getattr(client_obj, "id", None)) if client_obj else None,
        )

        quote = Quote.objects.create(owner=owner, **validated_data, subtotal=ZERO, tax_total=ZERO, total=ZERO)
        _qlog(self, logging.DEBUG, "quote.created", quote_id=str(getattr(quote, "id", None)))

        subtotal, tax_total = _create_items_and_compute_totals(self, quote, items, owner)

        discount_total = quantize_money(Decimal(str(validated_data.get("discount_total", ZERO) or ZERO)))
        total = quantize_money(subtotal + tax_total - discount_total)

        Quote.objects.filter(pk=quote.pk).update(
            subtotal=subtotal, tax_total=tax_total, discount_total=discount_total, total=total
        )
        quote.refresh_from_db()

        _qlog(
            self,
            logging.INFO,
            "quote.create.finish",
            quote_id=str(getattr(quote, "id", None)),
            subtotal=str(quote.subtotal),
            tax_total=str(quote.tax_total),
            discount_total=str(quote.discount_total),
            total=str(quote.total),
        )

        return quote

    @transaction.atomic
    def update(self, instance: Quote, validated_data: dict) -> Quote:
        # ⚠️ On veut savoir si 'items' est présent ou non dans le payload brut
        items_field_provided = "items" in (self.initial_data or {})
        # Si présent, on lit sa valeur validée (peut être []), sinon on laisse à None
        items = validated_data.pop("items", None) if items_field_provided else None

        request = self.context["request"]
        owner = request.user

        _qlog(
            self,
            logging.INFO,
            "quote.update.start",
            quote_id=str(getattr(instance, "id", None)),
            owner_id=getattr(owner, "id", None),
            items_field_provided=items_field_provided,
            items_count=(len(items) if isinstance(items, list) else None),
        )

        # --- Reassignation éventuelle du client ---
        new_client = validated_data.get("client", None)
        if new_client is not None and new_client != instance.client:
            if getattr(new_client, "owner_id", None) != getattr(owner, "id", None):
                _qlog(
                    self,
                    logging.WARNING,
                    "quote.update.client.forbidden",
                    quote_id=str(getattr(instance, "id", None)),
                    new_client_id=str(getattr(new_client, "id", None)),
                    owner_id=getattr(owner, "id", None),
                )
                raise ValidationError({"client": "You do not own this client."})
            _qlog(
                self,
                logging.INFO,
                "quote.update.client.reassigned",
                quote_id=str(getattr(instance, "id", None)),
                old_client_id=str(getattr(instance.client, "id", None)) if instance.client else None,
                new_client_id=str(getattr(new_client, "id", None)),
            )
            instance.client = new_client

        # --- Patch des champs du client lié ---
        client_patch = self.initial_data.get("client_update", None)
        if client_patch:
            _qlog(
                self,
                logging.INFO,
                "client.update.in_update",
                quote_id=str(getattr(instance, "id", None)),
                client_id=str(getattr(instance.client, "id", None)) if instance.client else None,
            )
            self._apply_client_update(instance.client, client_patch, requester=owner)

        # --- Autres champs du header (sans re-set de client) ---
        for attr, val in validated_data.items():
            if attr == "client":
                continue
            setattr(instance, attr, val)
        instance.save()

        # --- Gestion des lignes selon présence de 'items' dans le payload ---
        if items_field_provided:
            # On remplace entièrement (ou vide) les lignes
            deleted_count, _ = instance.items.all().delete()
            _qlog(
                self, logging.DEBUG, "quote.lines.cleared", quote_id=str(getattr(instance, "id", None)), deleted=deleted_count
            )

            if items and len(items) > 0:
                # Recréation depuis le payload
                subtotal, tax_total = _create_items_and_compute_totals(self, instance, items, owner)
                _qlog(
                    self,
                    logging.INFO,
                    "quote.lines.replaced",
                    quote_id=str(getattr(instance, "id", None)),
                    new_count=len(items),
                    subtotal=str(subtotal),
                    tax_total=str(tax_total),
                )
            else:
                # items = [] → tout est vide
                subtotal = ZERO
                tax_total = ZERO
                _qlog(self, logging.INFO, "quote.lines.empty_after_update", quote_id=str(getattr(instance, "id", None)))
        else:
            # On conserve les lignes existantes et on recalcule depuis la DB
            # (profite d'un éventuel prefetch; sinon simple agrégat Python)
            existing = list(instance.items.all())
            subtotal = quantize_money(sum((l.pre_tax_total() for l in existing), ZERO))
            tax_total = quantize_money(sum((l.tax_amount() for l in existing), ZERO))
            _qlog(
                self,
                logging.INFO,
                "quote.lines.preserved",
                quote_id=str(getattr(instance, "id", None)),
                existing_count=len(existing),
                subtotal=str(subtotal),
                tax_total=str(tax_total),
            )

        # --- Totaux finaux (on conserve discount_total existant si non fourni en header) ---
        discount_total = quantize_money(Decimal(str(getattr(instance, "discount_total", ZERO) or ZERO)))
        total = quantize_money(subtotal + tax_total - discount_total)

        Quote.objects.filter(pk=instance.pk).update(
            subtotal=subtotal, tax_total=tax_total, discount_total=discount_total, total=total
        )
        instance.refresh_from_db()

        _qlog(
            self,
            logging.INFO,
            "quote.update.finish",
            quote_id=str(getattr(instance, "id", None)),
            subtotal=str(instance.subtotal),
            tax_total=str(instance.tax_total),
            discount_total=str(instance.discount_total),
            total=str(instance.total),
            items_field_provided=items_field_provided,
        )

        return instance


# --------------------------------------------------------------------------------------
# Read serializer (inchangé)
# --------------------------------------------------------------------------------------
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


# --------------------------------------------------------------------------------------
# PDF preview serializer
# --------------------------------------------------------------------------------------
class QuotePreviewLineSerializer(serializers.Serializer):
    designation = serializers.CharField(required=False)
    description = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    quantity = serializers.FloatField(min_value=0.000001)
    unit_price = serializers.FloatField(min_value=0.0)
    tax_rate = serializers.FloatField(required=False, allow_null=True)  # 0.2 => 20% (fraction UI)
    discount = serializers.FloatField(required=False, min_value=0.0)


class QuotePreviewPayloadSerializer(serializers.Serializer):
    seller = serializers.DictField()
    client = serializers.DictField()
    meta = serializers.DictField()
    lines = QuotePreviewLineSerializer(many=True)
    branding = serializers.DictField(required=False)

    def validate(self, data):
        """Only normalize the data, do not validate the data."""
        normalized_lines = []
        for raw in data["lines"]:
            line = dict(raw)

            # designation fallback
            if not line.get("designation"):
                alt = line.get("name")
                if alt:
                    line["designation"] = str(alt)
            if not line.get("designation"):
                raise serializers.ValidationError("Designation/name is required for each line.")

            # tax_rate fallback
            tr = line.get("tax_rate", None)
            if tr is not None:
                tr = float(tr)
                if tr < 0:
                    tr = 0.0
                if tr > 1.0:
                    tr = tr / 100.0
                line["tax_rate"] = tr
            else:
                line["tax_rate"] = None

            # discount fallback
            if "discount" in line and line["discount"] is not None:
                line["discount"] = float(line["discount"])
                if line["discount"] < 0:
                    line["discount"] = 0.0

            line["quantity"] = float(line["quantity"])
            line["unit_price"] = float(line["unit_price"])

            normalized_lines.append(line)
        data["lines"] = normalized_lines
        return data
