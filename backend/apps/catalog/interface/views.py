from curses.ascii import isdigit
import django_filters
import logging
from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import filters as drf_filters
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from django_filters import rest_framework as django_filters
from apps.catalog.models import Area, Prestation
from apps.core.permissions import IsAuthenticatedReadOnly
from .filters import PrestationFilter
from .serializers import AreaSerializer, PrestationSerializer

logging = logging.getLogger(__name__)

class CatalogBaseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ViewSet de base pour les catalogues.
    """
    permission_classes = [
        AllowAny,
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
    queryset = Prestation.objects.select_related("area").all().order_by("area__name", "name")
    serializer_class = PrestationSerializer
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter, django_filters.DjangoFilterBackend]
    filterset_class = PrestationFilter   # <-- use filterset_class (not filter_class)
    search_fields = ["name", "description"]
    ordering_fields = ["name", "area", "status", "weight_days", "default_rate_cents", "id"]
    ordering = ["area", "name"]

    def get_queryset(self):
        # méthode defensive : loggue les params, essaye de filtrer ids/area/professional_user,
        # et en cas d'erreur retourne le queryset de base au lieu de laisser planter (500).
        try:
            logging.debug(
                "PrestationViewSet.get_queryset called by user=%s params=%s",
                getattr(self.request.user, "id", None),
                dict(self.request.query_params),
            )
            qs = super().get_queryset()

            # support ?ids=1,2,3 or repeated ?ids=1&ids=2
            ids_params = self.request.query_params.getlist("ids")
            if ids_params:
                ids_list = []
                for chunk in ids_params:
                    for part in str(chunk).split(","):
                        part = part.strip()
                        if part.isdigit():
                            ids_list.append(int(part))
                if ids_list:
                    return qs.filter(id__in=ids_list)

            # support ?area=15 (exact match)
            area = self.request.query_params.get("area")
            if area:
                try:
                    area_id = int(area)
                    qs = qs.filter(area_id=area_id)
                except (ValueError, TypeError):
                    logging.debug("Ignored invalid area param: %r", area)

            # support filtering by professional_user (existing behaviour)
            prof_id = self.request.query_params.get("professional_user")
            if prof_id:
                return qs.filter(Q(professional_user__isnull=True) | Q(professional_user_id=prof_id))

            return qs

        except Exception:
            # log the full exception with stacktrace to help debugging
            logging.exception("Error in PrestationViewSet.get_queryset, returning base queryset")
            try:
                return super().get_queryset()
            except Exception:
                # last resort: return an empty queryset (prevents 500)
                logging.exception("Failed to return super().get_queryset() as fallback, returning empty queryset")
                return Prestation.objects.none()

    def list(self, request, *args, **kwargs):
        logging.info("Prestation list requested user=%s params=%s",
                     getattr(request.user, "id", None),
                     dict(request.query_params))
        return super().list(request, *args, **kwargs)
