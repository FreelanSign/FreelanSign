# apps/catalog/filters.py
import django_filters
from django_filters import rest_framework as filters

from apps.catalog.models import Prestation


class PrestationFilter(filters.FilterSet):
    # area param expects a single id (exact match)
    area = django_filters.NumberFilter(field_name="area_id", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = Prestation
        fields = ["area", "status", "weight_days"]
