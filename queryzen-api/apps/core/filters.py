# pylint: disable=C0114
from apps.core.models import Zen

from django_filters import rest_framework as filters


class QueryZenFilter(filters.FilterSet):
    class Meta:
        model = Zen
        fields = ('name', 'version', 'collection', 'state')


class ZenFilter(filters.FilterSet):
    class Meta:
        model = Zen
        fields = ('version', 'state')
