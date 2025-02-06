import re

import celery.exceptions
from apps.core.exceptions import ZenAlreadyExistsError, ExecutionEngineException, MissingParametersException
from apps.core.filters import QueryZenFilter
from apps.core.models import Zen
from apps.core.serializers import (
    ZenSerializer,
    CreateZenSerializer,
    ExecuteZenSerializer
)
from apps.core.tasks import run_query

from django.conf import settings
from django.shortcuts import get_object_or_404

from django_filters import rest_framework as filters

from rest_framework import views
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status

from queryzen_api.celery import is_execution_engine_working


# GET /zen?collection=main&version=1
class ZenFilterViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Special view that breaks the REST pattern, it only accepts GET requests and has all kinds of
    filters via query parameters.

    Check ``QueryZenFilter.Meta.fields`` to see the available ones.
    """
    queryset = Zen.objects.all()
    serializer_class = ZenSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = QueryZenFilter


class ZenViewSet(views.APIView):

    def _validate_parameters_replacement(self, zen: Zen, parameters: dict) -> None:
        """
        Validate that given parameters and zen query parameters match.

        Regex explanation:
        (:) -> Search character :
        (w+) -> Catch one or more letters, numbers... what is the param name
        """
        required_parameters = re.findall(r':(\w+)', zen.query)
        if missing_params := [param for param in required_parameters if param not in parameters]:
            raise MissingParametersException(f'Missing required parameters: {missing_params}')

    def get(self, request, collection: str, name: str, version: str):
        """
        Get a Zen.
        """
        queryset = Zen.filter_by(collection=collection,
                                 name=name,
                                 version=version)
        objects = get_object_or_404(queryset)

        return Response(ZenSerializer(objects, many=False).data)

    def post(self, request, collection, name, version):
        """Runs a Zen in the backend."""
        serializer = ExecuteZenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        zen = get_object_or_404(
            Zen,
            collection=collection,
            name=name,
            version=version,
        )

        self._validate_parameters_replacement(zen, serializer.validated_data['parameters'])
        # Todo: Handle if Zen does not receive the params it needs to run

        is_engine_working, error_msg = is_execution_engine_working()
        if not is_engine_working:
            raise ExecutionEngineException(detail=error_msg)
        try:
            async_job = run_query.delay(
                serializer.validated_data['database'],
                zen.pk,
                serializer.validated_data['parameters']
            )
            timeout = serializer.validated_data.get('timeout', getattr(settings, 'ZEN_TIMEOUT'))
            query_result = async_job.get(timeout)
            return Response(query_result)
        except Exception as e:
            print(type(e))
            return Response(f'Running a Zen resulted in an uncaught exception: {e}',
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, collection: str, name: str, version: str):
        """
        Create a Zen.
        """
        serializer = CreateZenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if version != 'latest':
            # If version is not 'latest' (aka automatically handed by us),
            # check that it does not exist. If 'latest', we'll pick the
            # latest object and add one to its version, so we'll never collide.
            queryset = Zen.filter_by(collection=collection,
                                     name=name,
                                     version=version)
            if queryset.exists():
                raise ZenAlreadyExistsError()

        zen = Zen(
            collection=collection,
            name=name,
            version=version,
            **serializer.validated_data
        )
        zen.save()
        return Response(ZenSerializer(zen).data)

    def delete(self, request, collection: str, name: str, version: str):
        zen = get_object_or_404(
            Zen,
            collection=collection,
            name=name,
            version=version
        )
        zen.delete()
        return Response([], status=status.HTTP_200_OK)
