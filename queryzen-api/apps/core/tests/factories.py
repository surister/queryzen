from factory.django import DjangoModelFactory

from apps.core.models import QueryZen


class QueryZenFactory(DjangoModelFactory):
    class Meta:
        model = QueryZen
