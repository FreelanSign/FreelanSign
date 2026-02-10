# apps/quote/interface/filter.py
import django_filters as filters

from apps.quote.models import Quote


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class QuoteFilter(filters.FilterSet):
    status = CharInFilter(field_name="status", lookup_expr="in")
    issue_date = filters.DateFilter(field_name="issue_date", lookup_expr="gte")
    issue_date_before = filters.DateFilter(field_name="issue_date", lookup_expr="lte")

    class Meta:
        model = Quote
        fields = ["status", "client"]
