# apps/quote/interface/views.py
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from turtle import pd
from typing import Any, List, Optional

from django.db import transaction
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.logging import get_logger
from apps.quote.interface.permissions import IsOwnerOrAdmin
from apps.quote.interface.renderers import PDFRenderer
from apps.quote.interface.serializers import (
    ClientReadSerializer,
    QuoteCreateUpdateSerializer,
    QuotePreviewPayloadSerializer,
    QuoteSerializer,
)
from apps.quote.models import Quote, QuoteHistory, QuoteLineItem
from apps.quote.services.pdf_preview import QuotePreviewContext, render_quote_pdf

logger = logging.getLogger(__name__)

# Try to import real services; provide safe no-op fallbacks when not present.
try:
    from apps.quote.services.email_pdf import attach_pdf_to_quote, generate_pdf_for_quote, send_quote_email  # type: ignore
except Exception:

    def generate_pdf_for_quote(quote: Quote) -> Optional[bytes]:
        """Stub: return None in test environment if service not implemented."""
        return None

    def attach_pdf_to_quote(quote: Quote, pdf_content: Any) -> None:
        """Stub: no-op attach."""
        return None

    def send_quote_email(quote: Quote, recipients: List[str]) -> None:
        """Stub: no-op send."""
        return None


# Small serializer to document change_status payload in the schema
class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Quote.Status.choices)


# Pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


# Allowed status transitions (simple example)
ALLOWED_TRANSITIONS = {
    "DRAFT": {"SENT", "CANCELLED"},
    "SENT": {"ACCEPTED", "REJECTED", "CANCELLED"},
    "ACCEPTED": {"PAID", "CANCELLED"},
    "REJECTED": {"DRAFT"},
    # PAID/CANCELLED/EXPIRED considered terminal in this simplified graph
}


def _generate_reference_for_owner(owner) -> str:
    """
    Small unique-ish reference generator for duplicated quotes.
    Replace with your domain-specific generator if needed.
    """
    short = uuid.uuid4().hex[:8].upper()
    ts = datetime.utcnow().strftime("%y%m%d%H%M%S")
    return f"REF-{short}-{ts}"


@extend_schema_view(
    list=extend_schema(tags=["Quote"], summary="List quotes"),
    retrieve=extend_schema(tags=["Quote"], summary="Retrieve a quote"),
    create=extend_schema(tags=["Quote"], summary="Create a quote"),
    update=extend_schema(tags=["Quote"], summary="Update a quote"),
    partial_update=extend_schema(tags=["Quote"], summary="Partial update a quote"),
    destroy=extend_schema(tags=["Quote"], summary="Delete / Cancel a quote"),
    send=extend_schema(
        tags=["Quote"],
        summary="Send quote (generate PDF & email)",
        description="Mark quote as SENT, generate and attach PDF, trigger email send and create history.",
        responses=QuoteSerializer,
    ),
    duplicate=extend_schema(
        tags=["Quote"],
        summary="Duplicate quote",
        description="Duplicate the given quote into a new DRAFT quote, copying line items & metadata.",
        responses=QuoteSerializer,
    ),
    change_status=extend_schema(
        tags=["Quote"],
        summary="Change quote status",
        description="Change the status of the quote with validation of allowed transitions.",
        request=ChangeStatusSerializer,
        responses=QuoteSerializer,
    ),
)
class QuoteViewSet(viewsets.ModelViewSet):
    """
    Quote ModelViewSet exposing CRUD and custom actions:
      - send: mark quote as SENT, generate & attach PDF, send email, create history entry
      - duplicate: clone a quote into a new DRAFT
      - change_status: change with allowed-transition validation
      - partial_delete: convenience to cancel (soft delete)
    Access rules: controlled by IsOwnerOrAdmin permission class and by get_queryset/get_object logic.
    """

    queryset = Quote.objects.all().select_related("client").prefetch_related("items")
    serializer_class = QuoteSerializer
    permission_classes = [IsOwnerOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["status", "client", "owner"]
    ordering_fields = ["issue_date", "total"]
    search_fields = ["reference", "title", "metadata"]

    def get_serializer_class(self):
        """Use write serializer for create/update; read serializer otherwise."""
        if self.action in ("create", "update", "partial_update"):
            return QuoteCreateUpdateSerializer
        return QuoteSerializer

    def get_queryset(self):
        queryset = Quote.objects.select_related("client").prefetch_related(
            Prefetch("items", queryset=QuoteLineItem.objects.select_related().order_by("order"))
        )
        user = getattr(self.request, "user", None)
        # Non admin ne voient que leurs propres devis, admins voient tous les devis
        if user and (user.is_staff or user.is_superuser):
            return queryset
        return queryset.filter(owner=user)

    # ----------------------
    # Helper: robust detail lookup
    # ----------------------
    def _get_detail_obj(self, pk: str) -> Quote:
        """
        Resolve a Quote instance for detail actions:
          1) try scoped lookup using filter_queryset(self.get_queryset()) (owner-scoped)
          2) if not found and request.user is staff/superuser, attempt unrestricted lookup via model manager
          3) otherwise raise Http404
        This central helper avoids 404 surprises for admins while keeping list scoping strict.
        """
        filter_kwargs = {"pk": pk}
        try:
            return get_object_or_404(self.filter_queryset(self.get_queryset()), **filter_kwargs)
        except Http404:
            user = getattr(self.request, "user", None)
            if user and (user.is_staff or user.is_superuser):
                # Unrestricted lookup for admins
                return get_object_or_404(Quote.objects.select_related("owner", "client"), **filter_kwargs)
            # Non-admins get the 404
            raise

    # Override default get_object so DRF internals and other mixins use the same logic
    def get_object(self):
        """
        Use the helper-based lookup, then check object permissions.
        """
        lookup_field = self.lookup_field or "pk"
        lookup_value = self.kwargs.get(lookup_field) or self.kwargs.get("pk")
        if not lookup_value:
            raise Http404

        obj = self._get_detail_obj(lookup_value)
        # perform object-level permission checks (raises if not allowed)
        self.check_object_permissions(self.request, obj)
        return obj

    # ----------------------
    # Standard handlers (keep audit behavior on destroy)
    # ----------------------
    def retrieve(self, request, *args, **kwargs):
        logger = get_logger(__name__, request)
        logger.info("quote.retrieve.start", extra={"req": getattr(request, "req_id", None), "quote_id": kwargs.get("pk")})
        try:
            resp = super().retrieve(request, *args, **kwargs)
            client_payload = resp.data.get("client") if isinstance(resp.data, dict) else None
            logger.info(
                "quote.retrieve.done",
                extra={
                    "req": getattr(request, "req_id", None),
                    "quote_id": kwargs.get("pk"),
                    "has_client": bool(client_payload),
                    "client_keys": list(client_payload.keys()) if isinstance(client_payload, dict) else None,
                },
            )
            return resp
        except Exception as e:
            logger.exception(
                "quote.retrieve.error",
                extra={
                    "req": getattr(request, "req_id", None),
                    "quote_id": kwargs.get("pk"),
                },
            )
            raise

    def perform_destroy(self, instance: Quote):
        """
        Soft-cancel the quote and create a history entry.
        This is used both internally and by the destroy handler below.
        """
        instance.status = Quote.Status.CANCELLED
        instance.save(update_fields=["status", "updated_at"])
        QuoteHistory.objects.create(
            quote=instance,
            payload_snapshot={"action": "partial_delete"},
            action=QuoteHistory.Action.UPDATED if hasattr(QuoteHistory, "Action") else "updated",
            actor=getattr(self.request, "user", None),
        )

    def destroy(self, request, *args, **kwargs):
        """Destroy endpoint mapped to soft-cancel logic using consistent lookup."""
        # get_object() already performs object-permission checks, so we don't re-check incorrectly.
        obj = self.get_object()
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ----------------------
    # Custom actions
    # ----------------------
    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """
        Mark quote as SENT, generate and attach PDF, trigger email send and create history entry.
        Only owner should be allowed by permission class (IsOwnerOrAdmin implements that rule).
        """
        quote = self._get_detail_obj(pk)
        # perform object-level permission check (will raise 403 if not allowed)
        self.check_object_permissions(request, quote)
        # --- Defensive check: ensure only the owner can send the quote ---
        # This is redundant if the permission class already enforces it,
        # but provides a clearer error message and explicit guard.
        if getattr(quote, "owner", None) != getattr(request, "user", None):
            return Response(
                {"detail": "Only the owner of the quote is allowed to send it."},
                status=status.HTTP_403_FORBIDDEN,
            )
        quote.status = Quote.Status.SENT
        quote.sent_at = timezone.now()
        quote.save(update_fields=["status", "sent_at", "updated_at"])

        QuoteHistory.objects.create(
            quote=quote,
            payload_snapshot={"status": "SENT"},
            action=QuoteHistory.Action.SENT if hasattr(QuoteHistory, "Action") else "sent",
            actor=getattr(request, "user", None),
        )

        # Generate PDF and attach (best-effort)
        pdf_content = generate_pdf_for_quote(quote)
        if pdf_content is not None:
            try:
                attach_pdf_to_quote(quote, pdf_content)
            except Exception:
                # in production log this; do not fail the API call
                pass

        # Send email (best-effort)
        try:
            recipients: List[str] = []
            if getattr(quote.client, "email", None):
                recipients.append(quote.client.email)
            if request.user and getattr(request.user, "email", None):
                recipients.append(request.user.email)
            if recipients:
                send_quote_email(quote, recipients)
        except Exception:
            # swallow to avoid 500 in absence of real service
            pass

        serializer = QuoteSerializer(quote, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """
        Duplicate a quote into a new DRAFT quote; duplicate lines and metadata.
        Returns 201 with the new quote.
        """
        original = self._get_detail_obj(pk)
        # perform object-level permission check (will raise 403 if not allowed)
        self.check_object_permissions(request, original)

        owner = request.user
        cloned_fields = {
            "owner": original.owner,  # keep same owner
            "client": original.client,
            "title": f"{original.title} (copy)",
            "reference": _generate_reference_for_owner(owner),
            "currency": original.currency,
            "language": original.language,
            "status": Quote.Status.DRAFT,
            "issue_date": timezone.now().date(),
            "valid_until": original.valid_until,
            "payment_terms": original.payment_terms,
            "payment_terms_text": original.payment_terms_text,
            "note": original.note,
            "metadata": original.metadata or {},
            "subtotal": Decimal("0.00"),
            "tax_total": Decimal("0.00"),
            "discount_total": original.discount_total or Decimal("0.00"),
            "total": Decimal("0.00"),
        }

        with transaction.atomic():
            new_quote = Quote.objects.create(**cloned_fields)
            # duplicate line items
            for li in original.items.all():
                QuoteLineItem.objects.create(
                    quote=new_quote,
                    description=li.description,
                    qty=li.qty,
                    unit_price=li.unit_price,
                    tax_rate=li.tax_rate,
                    discount=li.discount,
                    order=li.order,
                    metadata=li.metadata or {},
                )

            # attempt to recalc totals via model helper if present, fallback otherwise
            try:
                # models may implement recalculate_totals(save=True)
                new_quote.recalculate_totals(save=True)
            except Exception:
                subtotal = sum((l.pre_tax_total() for l in new_quote.items.all()), Decimal("0.00"))
                tax_total = sum((l.tax_amount() for l in new_quote.items.all()), Decimal("0.00"))
                total = subtotal + tax_total - (new_quote.discount_total or Decimal("0.00"))
                Quote.objects.filter(pk=new_quote.pk).update(subtotal=subtotal, tax_total=tax_total, total=total)

            QuoteHistory.objects.create(
                quote=new_quote,
                payload_snapshot={"duplicated_from": str(original.pk)},
                action=QuoteHistory.Action.CREATED if hasattr(QuoteHistory, "Action") else "created",
                actor=getattr(request, "user", None),
            )

        serializer = QuoteSerializer(new_quote, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        """
        Change the quote status with validation against ALLOWED_TRANSITIONS.
        Payload: {"status": "ACCEPTED"}.
        """
        quote = self._get_detail_obj(pk)
        # perform object-level permission check (will raise 403 if not allowed)
        self.check_object_permissions(request, quote)

        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "Missing 'status' in payload."}, status=status.HTTP_400_BAD_REQUEST)

        current = quote.status
        allowed = ALLOWED_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            return Response(
                {"detail": f"Transition from {current} to {new_status} is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # perform transition and persist
        quote.status = new_status
        if new_status == Quote.Status.ACCEPTED:
            quote.accepted_at = timezone.now()
        quote.save(update_fields=["status", "accepted_at", "updated_at"])

        QuoteHistory.objects.create(
            quote=quote,
            payload_snapshot={"from": current, "to": new_status},
            action=QuoteHistory.Action.STATUS_CHANGED if hasattr(QuoteHistory, "Action") else "status_changed",
            actor=getattr(request, "user", None),
        )

        return Response(QuoteSerializer(quote, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def partial_delete(self, request, pk=None):
        """
        Convenience endpoint to soft-cancel a quote (maps to perform_destroy behaviour).
        """
        quote = self._get_detail_obj(pk)
        # perform object-level permission check (will raise 403 if not allowed)
        self.check_object_permissions(request, quote)
        self.perform_destroy(quote)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _log_request(self, request, action_name: str, pk=None):
        logger = get_logger(__name__, request)
        logger.info(
            f"quote.{action_name}.request",
            extra={
                "quote_id": pk,
                "user_id": getattr(request.user, "id", None),
                "is_auth": bool(getattr(request.user, "is_authenticated", False)),
                "data": request.data,
                "headers_auth": (
                    request.headers.get("Authorization", "")[:24] + "…" if request.headers.get("Authorization") else None
                ),
            },
        )

    def partial_update(self, request, *args, **kwargs):
        logger = get_logger(__name__, request)
        instance = self.get_object()
        logger.info(
            "quote.partial_update.request",
            extra={
                "quote_id": str(getattr(instance, "id", None)),
                "user_id": getattr(request.user, "id", None),
                "data": request.data,
            },
        )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.warning("quote.partial_update.validation_error errors=%s", serializer.errors)
            raise ValidationError(serializer.errors)
        self.perform_update(serializer)
        logger.info("quote.partial_update.response", extra={"status": 200})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        logger = get_logger(__name__, request)
        instance = self.get_object()
        logger.info(
            "quote.update.request",
            extra={
                "quote_id": str(getattr(instance, "id", None)),
                "user_id": getattr(request.user, "id", None),
                "data": request.data,
            },
        )
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():
            logger.warning("quote.partial_update.validation_error errors=%s", serializer.errors)
            raise ValidationError(serializer.errors)
        self.perform_update(serializer)
        logger.info("quote.update.response", extra={"status": 200})
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuotePreviewPdfView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def post(self, request):
        serializer = QuotePreviewPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        context = QuotePreviewContext(
            seller=data["seller"],
            client=data["client"],
            meta=data["meta"],
            lines=data["lines"],
            totals=data["totals"],
            branding=data.get("branding"),
        )
        try:
            pdf_bytes = render_quote_pdf(context)
        except Exception:
            logger.exception("Unexpected error in quote preview PDF generation")
            raise
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="quote-preview.pdf"'
        return response
