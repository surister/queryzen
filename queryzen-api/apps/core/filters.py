from apps.core.models import QueryZen

from django_filters import rest_framework as filters


class QueryZenFilter(filters.FilterSet):
    class Meta:
        model = QueryZen
        fields = ('name', 'version', 'collection', 'state')


class ZenFilter(filters.FilterSet):
    class Meta:
        model = QueryZen
        fields = ('version', 'state')
