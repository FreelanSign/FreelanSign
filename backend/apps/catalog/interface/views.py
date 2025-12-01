# apps/catalog/interface/views.py
"""
Views API pour le module catalog.
Couche interface: mapping HTTP ⇄ Use Cases.
"""
import logging

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters as drf_filters
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.catalog.adapters.persistence.django_prestation_repository import (
    DjangoAreaRepository,
    DjangoPrestationRepository,
)
from apps.catalog.application.dto.prestation_inputs import (
    GetPrestationInput,
    ListPrestationsInput,
)
from apps.catalog.application.usecases.get_prestation import GetPrestation
from apps.catalog.application.usecases.list_prestations import ListPrestations
from apps.catalog.models import Area, Prestation
from apps.core.permissions import IsAuthenticatedReadOnly

from .error_handler import CatalogErrorHandler
from .serializers import AreaSerializer, PrestationSerializer

logger = logging.getLogger(__name__)


class CatalogBaseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet de base pour les catalogues (read-only)."""

    permission_classes = [IsAuthenticatedReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "catalog"


@extend_schema(
    tags=["Catalog"],
    summary="Lister les domaines d'activité (areas)",
    parameters=[
        OpenApiParameter(name="search", description="Recherche par nom", required=False, type=str),
    ],
)
class AreaViewSet(CatalogBaseViewSet):
    """
    ViewSet pour les domaines d'activité (areas).
    Implémentation classique (pas de use case pour ce cas simple).
    """

    queryset = Area.objects.all().order_by("name")
    serializer_class = AreaSerializer
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "id"]
    ordering = ["name"]


@extend_schema(
    tags=["Catalog"],
    summary="Lister les prestations",
    parameters=[
        OpenApiParameter(name="area", description="Filtrer par ID d'Area", required=False, type=int),
        OpenApiParameter(name="status", description="Filtrer par statut (DRAFT, ACTIVE, ARCHIVED)", required=False, type=str),
        OpenApiParameter(name="search", description="Recherche sur nom/description", required=False, type=str),
        OpenApiParameter(name="ids", description="Filtrer par liste d'IDs (comma-separated)", required=False, type=str),
        OpenApiParameter(
            name="ordering",
            description="Tri: name, -name, area, status, weight_days, default_rate_cents",
            required=False,
            type=str,
        ),
    ],
)
class PrestationViewSet(CatalogBaseViewSet):
    """
    ViewSet pour les prestations.
    Utilise Clean Architecture avec use cases.
    """

    queryset = Prestation.objects.select_related("area").all()
    serializer_class = PrestationSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Injection de dépendances
        self.prestation_repository = DjangoPrestationRepository()
        self.list_prestations_usecase = ListPrestations(self.prestation_repository)
        self.get_prestation_usecase = GetPrestation(self.prestation_repository)

    def list(self, request, *args, **kwargs):
        """Liste les prestations via le use case."""
        logger.info("PrestationViewSet.list: user=%s params=%s", getattr(request.user, "id", None), dict(request.query_params))

        try:
            # Construction du DTO d'entrée
            input_dto = self._build_list_input(request)

            # Exécution du use case
            result = self.list_prestations_usecase.execute(input_dto)

            page = self.paginate_queryset(result.prestations)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(result.prestations, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            return CatalogErrorHandler.handle_error(e)

    def retrieve(self, request, *args, **kwargs):
        """Récupère une prestation via le use case."""
        prestation_id = int(kwargs.get("pk"))

        logger.info("PrestationViewSet.retrieve: user=%s prestation_id=%s", getattr(request.user, "id", None), prestation_id)

        try:
            # Construction du DTO d'entrée
            input_dto = GetPrestationInput(prestation_id=prestation_id)

            # Exécution du use case
            result = self.get_prestation_usecase.execute(input_dto)

            # Conversion du ViewModel en réponse API
            serializer = self.get_serializer(result)

            return Response(serializer.data, status=200)

        except Exception as e:
            return CatalogErrorHandler.handle_error(e)

    def _build_list_input(self, request) -> ListPrestationsInput:
        """Construit le DTO d'entrée depuis les query params."""
        # Récupération des paramètres
        area_id = request.query_params.get("area")
        status = request.query_params.get("status")
        search = request.query_params.get("search")
        account_id = request.query_params.get("account") or request.query_params.get("professional_user")  # Phase 5.4
        ordering_param = request.query_params.get("ordering")
        ordering = None
        if ordering_param:
            ordering = [p.strip() for p in str(ordering_param).split(",") if p.strip()]

        # Parsing des IDs (support "ids=1,2,3" ou "ids=1&ids=2")
        prestation_ids = None
        ids_params = request.query_params.getlist("ids")
        if ids_params:
            ids_list = []
            for chunk in ids_params:
                for part in str(chunk).split(","):
                    part = part.strip()
                    if part.isdigit():
                        ids_list.append(int(part))
            if ids_list:
                prestation_ids = ids_list

        # Conversion des types
        area_id_int = None
        if area_id:
            try:
                area_id_int = int(area_id)
            except (ValueError, TypeError):
                logger.debug("Invalid area param: %r", area_id)

        account_id_int = None
        if account_id:
            try:
                account_id_int = int(account_id)
            except (ValueError, TypeError):
                logger.debug("Invalid account param: %r", account_id)

        return ListPrestationsInput(
            area_id=area_id_int,
            status=status,
            search=search,
            account_id=account_id_int,
            prestation_ids=prestation_ids,
            ordering=ordering,
        )
