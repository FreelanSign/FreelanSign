import django_filters
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import filters as drf_filters
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from apps.catalog.models import Area, Prestation
from apps.core.permissions import IsAuthenticatedReadOnly

from .filters import PrestationFilter
from .serializers import AreaSerializer, PrestationSerializer


class CatalogBaseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ViewSet de base pour les catalogues.
    """

    permission_classes = [
        IsAuthenticatedReadOnly,
    ]  # read-only + auth
    throttle_classes = [
        ScopedRateThrottle,
    ]
    throttle_scope = "catalog"  # configuré dans settings


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
        OpenApiParameter(name="area", description="Filtrer par id d'Area", required=False, type=int, many=True),
        OpenApiParameter(name="status", description="Filtrer par statut (DRAFT, ACTIVE, ARCHIVED=", required=False, type=str),
        OpenApiParameter(name="search", description="Recherche sur nom/description", required=False, type=str),
        OpenApiParameter(
            name="ordering", description="Tri: name,-name,area,status,weight_days,default_rate_cents", required=False, type=str
        ),
    ],
)
class PrestationViewSet(CatalogBaseViewSet):
    """Viewset pour les prestations.

    Args:
        CatalogBaseViewSet (_type_): _description_
    """

    queryset = Prestation.objects.select_related("area").all().order_by("area__name", "name")
    serializer_class = PrestationSerializer
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter, django_filters.rest_framework.DjangoFilterBackend]
    filter_class = PrestationFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "area", "status", "weight_days", "default_rate_cents", "id"]
    ordering = ["area", "name"]
