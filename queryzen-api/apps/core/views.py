import http

import celery
from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound, MethodNotAllowed
from rest_framework.response import Response

from apps.core.filters import QueryZenFilter, ZenFilter
from apps.core.models import QueryZen
from apps.core.serializers import QueryZenSerializer, CreateZenSerializer, DeleteZenSerializer, CollectionsSerializer, \
    ExecuteZenSerializer
from apps.core.tasks import run_query

from django_filters import rest_framework as filters

from rest_framework import mixins, viewsets, status


class TransversalZenViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = QueryZen.objects.all()
    serializer_class = QueryZenSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = QueryZenFilter


class CollectionsViewSet(viewsets.ModelViewSet):
    queryset = QueryZen.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ZenFilter

    def _handle_request(self, request, collection_name, *args, **kwargs):
        if self.request.method == http.HTTPMethod.GET:
            return self._get_zens_given(collection_name, kwargs.get('zen_name'))
        if self.request.method == http.HTTPMethod.PUT:
            return self._create_zen(request, collection_name, kwargs.get('zen_name'))
        if self.request.method == http.HTTPMethod.DELETE:
            return self._delete_zen(request, collection_name, kwargs.get('zen_name'))
        if self.request.method == http.HTTPMethod.POST:
            return self._run_zen(request, collection_name, kwargs.get('zen_name'))
        raise MethodNotAllowed({'msg': f'{self.request.method} is not allowed'})

    def get_serializer_class(self):
        if self.action == 'list':
            return QueryZenSerializer
        if self.action == 'zen':
            if self.request.method == http.HTTPMethod.GET:
                return CreateZenSerializer
            if self.request.method == http.HTTPMethod.PUT:
                return CreateZenSerializer
            if self.request.method == http.HTTPMethod.DELETE:
                return DeleteZenSerializer
            if self.request.method == http.HTTPMethod.POST:
                return ExecuteZenSerializer

    def _run_zen(self, request, collection_name, zen_name):
        serializer = ExecuteZenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        zen = get_object_or_404(
            QueryZen,
            name=zen_name,
            collection=collection_name,
            version=serializer.data['version']
        )
        try:
            async_job = run_query.delay(
                serializer.validated_data['target'],
                zen.pk,
                serializer.validated_data['parameters']
            )
            query_result = async_job.get(timeout=getattr(settings, 'ZEN_TIMEOUT'))
            return Response(query_result)
        except Exception as e:
            return Response({'msg': f'{self.request.method} is timeout'}, status=status.HTTP_400_BAD_REQUEST)

    def _delete_zen(self, request, collection_name, zen_name):
        serializer = DeleteZenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not QueryZen.objects.filter(
                version=serializer.validated_data['version'],
                name=zen_name,
                collection=collection_name
        ).exists():
            raise NotFound()

        QueryZen.objects.filter(
            version=serializer.validated_data['version'],
            name=zen_name,
            collection=collection_name
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_zens_given(self, collection_name, zen_name):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(
            collection=collection_name,
            name=zen_name,
        )
        return Response(
            QueryZenSerializer(queryset, many=True).data,
        )

    def _create_zen(self, request, collection_name, zen_name):
        serializer = CreateZenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if QueryZen.objects.filter(
                name=zen_name,
                version=serializer.validated_data['version'],
                collection=collection_name
        ).exists():
            raise ValidationError(f'This zen already has a version {serializer.validated_data["version"]}')

        zen = QueryZen.objects.create(
            **serializer.validated_data,
            **{'name': zen_name, 'collection': collection_name}
        )

        return Response(QueryZenSerializer(zen).data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = QueryZen.objects.values('collection').annotate(zen_count=Count('name'))
        return Response(CollectionsSerializer(queryset, many=True).data)

    def retrieve(self, request, pk, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(
            collection=pk,
        )
        return Response(
            QueryZenSerializer(queryset, many=True).data,
        )

    @action(detail=True, methods=['get', 'put', 'delete', 'post'], url_path='zen/(?P<zen_name>[^/.]+)')
    def zen(self, request, pk, *args, **kwargs):
        return self._handle_request(request, pk, *args, **kwargs)
