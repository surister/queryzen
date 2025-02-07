# pylint: disable=C0114
import django_filters

from apps.core.models import Zen

from django_filters import rest_framework as filters


class QueryZenFilter(filters.FilterSet):
    executions__state = django_filters.CharFilter(field_name='executions__state',
                                                  lookup_expr='exact')

    class Meta:
        model = Zen
        fields = {
            'name': ['exact', 'contains'],
            'collection': ['exact', 'contains'],
            'version': ['exact', 'gt', 'lt'],
            'state': ['exact'],
            'executions__state': ['exact']
        }
