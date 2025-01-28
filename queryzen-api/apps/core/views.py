from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.filters import QueryZenFilter, ZenFilter
from apps.core.models import QueryZen
from apps.core.serializers import QueryZenSerializer, CreateZenSerializer

from django_filters import rest_framework as filters

from rest_framework import mixins, viewsets, status


class QueryZenViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = QueryZen.objects.all()
    serializer_class = QueryZenSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = QueryZenFilter


class CollectionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = QueryZen.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ZenFilter

    def get_serializer_class(self):
        if self.action == 'update':
            return CreateZenSerializer
        return QueryZenSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(
            collection=kwargs.get('collection_name'),
            name=kwargs.get('zen_name'),
        )
        return Response(
            QueryZenSerializer(queryset, many=True).data,
        )


class ZenApiView(APIView):
    def put(self, request, *args, **kwargs):
        serializer = CreateZenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        zen = QueryZen.objects.create(
            **serializer.validated_data,
            **{'name': kwargs.get('zen_name'), 'collection': kwargs.get('collection_name')}
        )

        return Response(QueryZenSerializer(zen).data, status=status.HTTP_201_CREATED)
