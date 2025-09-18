import django_filters

from apps.catalog.models import Prestation, PrestationStatus


class PrestationFilter(django_filters.FilterSet):
    area = django_filters.NumberFilter(field_name="area__id", lookup_expr="exact")
    status = django_filters.CharFilter(method="filter_status")

    def filter_status(self, queryset, name, value: str):
        if not value:
            return queryset
        value = value.strip().upper()
        # safe list of valid values:
        try:
            valid_values = [c.value for c in PrestationStatus]
        except Exception:
            # fallback: try using .values attribute if it exists
            valid_values = getattr(PrestationStatus, "values", tuple())
        if value in valid_values:
            return queryset.filter(status=value)
        # si statut invalide, retourner queryset vide ou ne rien filtrer selon ton choix :
        return queryset.none()

    class Meta:
        model = Prestation
        fields = ("area", "status")
