# apps/quote/interface/views.py
from __future__ import annotations

import logging
from textwrap import dedent
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from apps.quote.adapters.persistence.django_prestation_repository import DjangoPrestationRepository
from apps.quote.application.usecases.add_prestation_line import AddPrestationLineToQuote, AddPrestationLineInput
from apps.quote.adapters.rendering.pdf_context_presenter import preview_context
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
    QuoteCreateUpdateSerializer,
    QuotePreviewPayloadSerializer,
    QuoteSerializer,
)
from apps.quote.models import Quote, QuoteHistory, QuoteLineItem

# --- NEW: Clean Arch imports (use cases + adapters) -----------------------------------
from apps.quote.adapters.persistence.django_quote_repository import DjangoQuoteRepository  # type: ignore
from apps.quote.adapters.rendering.django_template_renderer import DjangoTemplateRenderer  # type: ignore
from apps.quote.adapters.pdf.playwright_generator import PlaywrightPdfGenerator  # type: ignore

from apps.quote.application.usecases.generate_preview import generate_preview
from apps.quote.application.usecases.send_quote import SendQuote  # type: ignore
from apps.quote.application.usecases.duplicate_quote import DuplicateQuote  # type: ignore
from apps.quote.application.usecases.change_status import ChangeStatus  # type: ignore
from apps.quote.application.usecases.download_pdf import DownloadPdf  # type: ignore

from apps.quote.application.dto.quote_inputs import PreviewPayloadDTO, LineItemInputDTO

logger = logging.getLogger(__name__)

# --- NEW: optional adapters (fallback stubs if not yet implemented) -------------------
try:
    from apps.quote.adapters.email.django_email_sender import DjangoEmailSender  # type: ignore
except Exception:
    class DjangoEmailSender:  # minimal stub
        def send_quote(self, *, recipients: list[str], subject: str, body_html: str, attachments: list[tuple[str, bytes]]):
            return None

try:
    from apps.quote.adapters.reference.django_reference_gen import DjangoReferenceGenerator  # type: ignore
except Exception:
    class DjangoReferenceGenerator:
        def new(self, owner_id) -> str:
            short = uuid.uuid4().hex[:8].upper()
            ts = datetime.utcnow().strftime("%y%m%d%H%M%S")
            return f"REF-{short}-{ts}"

# --------------------------------------------------------------------------------------

# Small serializer to document change_status payload in the schema
class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Quote.Status.choices)


# Pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


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
        description="Change the status of the quote with policy validation.",
        request=ChangeStatusSerializer,
        responses=QuoteSerializer,
    ),
)
class QuoteViewSet(viewsets.ModelViewSet):
    """
    Views minces : délèguent au coeur applicatif (use cases).
    """

    queryset = Quote.objects.all().select_related("client").prefetch_related("items")
    serializer_class = QuoteSerializer
    permission_classes = [IsOwnerOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["status", "client", "owner"]
    ordering_fields = ["issue_date", "total"]
    search_fields = ["reference", "title", "metadata"]

    # --- helpers clean ----------------------------------------------------------------
    def _repo(self) -> DjangoQuoteRepository:
        return DjangoQuoteRepository()

    def _renderer(self) -> DjangoTemplateRenderer:
        return DjangoTemplateRenderer()

    def _pdf(self) -> PlaywrightPdfGenerator:
        return PlaywrightPdfGenerator()

    def _mailer(self) -> DjangoEmailSender:
        return DjangoEmailSender()

    def _reference_gen(self) -> DjangoReferenceGenerator:
        return DjangoReferenceGenerator()

    def _prestations(self) -> DjangoPrestationRepository:
        return DjangoPrestationRepository()

    def _owner_vat_config_from_user(self, user) -> tuple[bool, Decimal]:
        profile = getattr(user, "profile", None)
        vat_exempt = bool(getattr(profile, "vat_exempt", False))
        default_rate = getattr(profile, "default_tax_rate", None)
        if default_rate is None:
            default_rate = Decimal("20.00")
        else:
            default_rate = Decimal(str(default_rate)).quantize(Decimal("0.01"))
        return vat_exempt, default_rate

    def _client_country_from_model(self, client) -> str | None:
        if not client:
            return None
        for key in ("country", "country_code", "billing_country"):
            val = getattr(client, key, None)
            if val:
                return str(val).upper()
        meta = getattr(client, "metadata", None)
        if isinstance(meta, dict):
            for key in ("country", "country_code", "billing_country"):
                if meta.get(key):
                    return str(meta[key]).upper()
        return None

    # ----------------------------------------------------------------------------------

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return QuoteCreateUpdateSerializer
        return QuoteSerializer

    def get_queryset(self):
        queryset = Quote.objects.select_related("client").prefetch_related(
            Prefetch("items", queryset=QuoteLineItem.objects.select_related().order_by("order"))
        )
        user = getattr(self.request, "user", None)
        if user and (user.is_staff or user.is_superuser):
            return queryset
        return queryset.filter(owner=user)

    def _get_detail_obj(self, pk: str) -> Quote:
        filter_kwargs = {"pk": pk}
        try:
            return get_object_or_404(self.filter_queryset(self.get_queryset()), **filter_kwargs)
        except Http404:
            user = getattr(self.request, "user", None)
            if user and (user.is_staff or user.is_superuser):
                return get_object_or_404(Quote.objects.select_related("owner", "client"), **filter_kwargs)
            raise

    def get_object(self):
        lookup_field = self.lookup_field or "pk"
        lookup_value = self.kwargs.get(lookup_field) or self.kwargs.get("pk")
        if not lookup_value:
            raise Http404
        obj = self._get_detail_obj(lookup_value)
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=["post"], url_path="add-prestation-line")
    def add_prestation_line(self, request, pk=None):
        """Add a prestation line to a quote."""
        quote = self._get_detail_obj(pk)
        self.check_object_permissions(request, quote)

        body = request.data or {}
        if "prestation_id" not in body:
            return Response({"detail": "Missing 'prestation_id' in payload."}, status=400)

        vat_exempt, default_rate = self._owner_vat_config_from_user(request.user)

        uc = AddPrestationLineToQuote(quotes=self._repo(), prestations=self._prestations())
        q, li = uc.execute(AddPrestationLineInput(
            quote_id=str(quote.pk),
            prestation_id=str(body["prestation_id"]),
            qty=(Decimal(str(body.get("qty", None))) if body.get("qty", None) is not None else None),
            tax_rate_pct=(Decimal(str(body.get("tax_rate_pct", None))) if body.get("tax_rate_pct", None) is not None else None),
            discount=(Decimal(str(body.get("discount", None))) if body.get("discount", None) is not None else None),
            order=body.get("order", 0),
            owner_vat_exempt=vat_exempt,
            owner_default_rate_pct=default_rate,
        ))
        from apps.quote.interface.serializers import QuoteSerializer
        return Response(QuoteSerializer(q, context={"request": request}).data, status=200)

    # ----------------------
    # Standard handlers
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
        except Exception:
            logger.exception(
                "quote.retrieve.error",
                extra={"req": getattr(request, "req_id", None), "quote_id": kwargs.get("pk")},
            )
            raise

    def perform_destroy(self, instance: Quote):
        instance.status = Quote.Status.CANCELLED
        instance.save(update_fields=["status", "updated_at"])
        QuoteHistory.objects.create(
            quote=instance,
            payload_snapshot={"action": "partial_delete"},
            action=QuoteHistory.Action.UPDATED,
            actor=getattr(self.request, "user", None),
        )

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ----------------------
    # Custom actions (CLEAN ARCH)
    # ----------------------
    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """
        Orchestration métier via use case SendQuote (PDF + mail + statut SENT + history).
        """
        # scope + permission
        quote = self._get_detail_obj(pk)
        self.check_object_permissions(request, quote)
        if getattr(quote, "owner", None) != getattr(request, "user", None):
            return Response({"detail": "Only the owner of the quote is allowed to send it."}, status=403)

        # policies context
        vat_exempt, default_rate = self._owner_vat_config_from_user(request.user)
        client_country = self._client_country_from_model(quote.client)

        # use case + adapters
        uc = SendQuote(
            repo=self._repo(),
            renderer=self._renderer(),
            pdf=self._pdf(),
            mailer=self._mailer(),
        )
        out_quote, _pdf_bytes = uc.execute(
            quote_id=str(quote.pk),
            owner_vat_exempt=vat_exempt,
            owner_default_rate_pct=default_rate,
            client_country=client_country,
            actor=request.user,
        )
        return Response(QuoteSerializer(out_quote, context={"request": request}).data, status=200)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """
        Clone un devis en DRAFT via use case DuplicateQuote.
        """
        original = self._get_detail_obj(pk)
        self.check_object_permissions(request, original)

        uc = DuplicateQuote(repo=self._repo(), reference_gen=self._reference_gen())
        with transaction.atomic():
            new_quote = uc.execute(quote_id=str(original.pk), actor=request.user)

        return Response(QuoteSerializer(new_quote, context={"request": request}).data, status=201)

    # TODO: Exception handler centralisé pour remplacer les try/catch et les gérer avec un decorator
    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        """
        Change le statut via policy (ChangeStatus use case).
        Payload: {"status": "..."}.
        """
        if "status" not in request.data:
            return Response({"detail": "Missing 'status' in payload."}, status=400)

        quote = self._get_detail_obj(pk)
        self.check_object_permissions(request, quote)

        uc = ChangeStatus(repo=self._repo())
        try:
            updated = uc.execute(quote_id=str(quote.pk), new_status=str(request.data["status"]), actor=request.user)
        except ValueError as e:  # transitions illégales
            return Response({"detail": str(e)}, status=400)

        return Response(QuoteSerializer(updated, context={"request": request}).data, status=200)

    @action(
        detail=True,
        methods=["get"],
        url_path="pdf",
        url_name="download-pdf",
        renderer_classes=[PDFRenderer, JSONRenderer, BrowsableAPIRenderer],
    )
    def download_pdf(self, request, pk=None):
        """
        Génère et renvoie le PDF (sans changer le statut) via use case DownloadPdf.
        """
        # scope + permission
        quote = self._get_detail_obj(pk)
        self.check_object_permissions(request, quote)

        # policy context
        vat_exempt, default_rate = self._owner_vat_config_from_user(request.user)
        client_country = self._client_country_from_model(quote.client)

        uc = DownloadPdf(repo=self._repo(), renderer=self._renderer(), pdf=self._pdf())
        pdf_bytes = uc.execute(
            quote_id=str(quote.pk),
            owner_vat_exempt=vat_exempt,
            owner_default_rate_pct=default_rate,
            client_country=client_country,
            actor=request.user,
        )
        filename = f"Devis-{quote.reference}-{timezone.now().date()}.pdf".replace(" ", "-")
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Cache-Control"] = "no-store"
        return response

    # ----------------------
    # Update handlers
    # ----------------------
    def partial_update(self, request, *args, **kwargs):
        logger = get_logger(__name__, request)
        instance = self.get_object()
        logger.info(
            "quote.partial_update.request",
            extra={"quote_id": str(getattr(instance, "id", None)), "user_id": getattr(request.user, "id", None), "data": request.data},
        )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.warning("quote.partial_update.validation_error errors=%s", serializer.errors)
            raise ValidationError(serializer.errors)
        self.perform_update(serializer)
        logger.info("quote.partial_update.response", extra={"status": 200})
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        logger = get_logger(__name__, request)
        instance = self.get_object()
        logger.info(
            "quote.update.request",
            extra={"quote_id": str(getattr(instance, "id", None)), "user_id": getattr(request.user, "id", None), "data": request.data},
        )
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():
            logger.warning("quote.update.validation_error errors=%s", serializer.errors)
            raise ValidationError(serializer.errors)
        self.perform_update(serializer)
        logger.info("quote.update.response", extra={"status": 200})
        return Response(serializer.data, status=200)


class QuotePreviewPdfView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def post(self, request):
        # Validation of the payload
        serializer = QuotePreviewPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Context Policies
        # REFACTOR: @Bertrand2808: Créer un objet PolicyContext pour éviter la duplication de code

        vat_exempt, default_rate = QuoteViewSet._owner_vat_config_from_user(self, request.user)
        client_country = _client_country_from_payload(data.get("client"))

        # Mapper payload -> DTO (tax_rate en %)
        from decimal import Decimal as D
        lines_dto: list[LineItemInputDTO] = []
        for line in data["lines"]:
            raw_tr = line.get("tax_rate")
            tax_rate_pct = None
            if raw_tr is not None:
                raw = float(raw_tr)
                tax_rate_pct = D(str(raw * 100.0)) if raw <= 1.0 else D(str(raw))
            discount_val = line.get("discount")
            discount_dec = D(str(discount_val)) if discount_val is not None else None
            lines_dto.append(
                LineItemInputDTO(
                    description=str(line.get("designation") or line.get("name") or ""),
                    qty=D(str(line["quantity"])),
                    unit_price=D(str(line["unit_price"])),
                    discount=discount_dec,
                    tax_rate_pct=tax_rate_pct,
                )
            )

        dto = PreviewPayloadDTO(
            seller=data["seller"],
            client=data["client"],
            meta=data["meta"],
            lines=lines_dto,
            branding=data.get("branding"),
            owner_vat_exempt=vat_exempt,
            owner_default_rate_pct=default_rate,
            client_country=client_country,
        )
        try:
            vm = generate_preview(dto)
        except Exception as e:
            return Response({"code": "QUOTE_PREVIEW_VALIDATION", "detail": str(e)}, status=422)

        # Adapters: PDF Preview Renderer
        renderer = DjangoTemplateRenderer()
        pdfgen = PlaywrightPdfGenerator()
        try:
            html = renderer.render("quote/pdf/preview.html", vm)
            pdf_bytes = pdfgen.generate(html)
        except Exception as e:
            return Response({"code": "QUOTE_PREVIEW_RENDERING", "detail": str(e)}, status=503)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="quote-preview.pdf"'
        return response


# --- little helper kept for preview payload -------------------------------------------
def _client_country_from_payload(client_dict: dict | None) -> str | None:
    if not client_dict:
        return None
    for key in ("country", "country_code", "billing_country"):
        val = client_dict.get(key)
        if val:
            return str(val).upper()
    return None
