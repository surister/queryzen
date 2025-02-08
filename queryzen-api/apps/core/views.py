# pylint: disable=C0114
import logging
import re

from apps.core.exceptions import ZenAlreadyExistsError, ExecutionEngineError, \
    MissingParametersError, DatabaseDoesNotExistError
from apps.core.filters import QueryZenFilter
from apps.core.models import Zen, Execution
from apps.core.serializers import (
    ZenSerializer,
    CreateZenSerializer,
    ExecuteZenSerializer, ZenStatsSerializer
)
from apps.core.tasks import run_query

from django.conf import settings
from django.shortcuts import get_object_or_404

from django_filters import rest_framework as filters

from rest_framework import views
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status

from statistics import median


# from queryzen_api.celery import is_execution_engine_working


# GET /zen?collection=main&version=1
class ZenFilterViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Special view that breaks the REST pattern, it only accepts GET requests and has all kinds of
    filters via query parameters.

    Check ``QueryZenFilter.Meta.fields`` to see the available ones.
    """
    queryset = Zen.objects.all()
    serializer_class = ZenSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = QueryZenFilter


class ZenView(views.APIView):
    """View for handling Zen lifetimes. It follows the REST pattern.
    GET: Get a Zen.
    POST: Run a Zen.
    PUT: Create a Zen.
    DELETE: Delete a Zen.
    """

    def _validate_parameters_replacement(self, zen: Zen, parameters: dict) -> None:
        """Validate that given parameters and zen query parameters match.

        Regex explanation:
        (:) -> Search character :
        (w+) -> Catch one or more letters, numbers... what is the param name
        """
        required_parameters = re.findall(r':(\w+)', zen.query)
        if missing_params := [param for param in required_parameters if param not in parameters]:
            raise MissingParametersError(f'The Zen requires parameters'
                                         f' that were not supplied: {missing_params!r}')

    def get(self, request, collection: str, name: str, version: str):  # pylint: disable=W0613
        """Get a Zen."""
        queryset = Zen.filter_by(collection=collection,
                                 name=name,
                                 version=version)
        objects = get_object_or_404(queryset)
        return Response(ZenSerializer(objects, many=False).data)

    def post(self, request, collection, name, version):
        """Runs a Zen in the backend."""
        serializer = ExecuteZenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        zen = get_object_or_404(Zen,
                                collection=collection,
                                name=name,
                                version=version)
        self._validate_parameters_replacement(zen, serializer.validated_data['parameters'])

        is_engine_working, error_msg = True, ''  # is_execution_engine_working()
        if not is_engine_working:
            raise ExecutionEngineError(detail=error_msg)

        requested_database = serializer.validated_data['database']
        if not settings.ZEN_DATABASES.get(requested_database):
            raise DatabaseDoesNotExistError(f'The asked database {repr(requested_database)}'
                                            f' is not configured in the backed.')
        try:
            async_job = run_query.delay(requested_database,
                                        zen.pk,
                                        serializer.validated_data['parameters'])
            timeout = serializer.validated_data.get('timeout', getattr(settings, 'ZEN_TIMEOUT'))
            query_result = async_job.get(timeout)
            return Response(query_result)
        except Exception as e:  # pylint: disable=W0718 TODO Fix exception (Make a better one)
            logging.warning(e)
            return Response(f'Running a Zen resulted in an uncaught exception: {e}',
                            status=status.HTTP_408_REQUEST_TIMEOUT)

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

        zen = Zen(collection=collection,
                  name=name,
                  version=version,
                  **serializer.validated_data)
        zen.save()
        return Response(ZenSerializer(zen).data)

    def delete(self, request, collection: str, name: str, version: str):  # pylint: disable=W0613
        zen = get_object_or_404(Zen,
                                collection=collection,
                                name=name,
                                version=version)
        zen.delete()
        return Response([], status=status.HTTP_200_OK)


class ZenStatsAPIView(views.APIView):

    def get(self, request, collection: str, name: str, version: str):
        zen = get_object_or_404(
            Zen,
            collection=collection,
            name=name,
            version=version
        )

        response_data = ZenStatsSerializer(
            {
                'total_executions': zen.executions.count(),
                'failed_executions': zen.failed_executions,
                'successful_executions': zen.executions.count() - zen.failed_executions,
                'average_execution_time_ms': zen.average_execution_time,
                'median_execution_time_ms': median(zen.executions.values_list('execution_time_in_ms',
                                                                              flat=True)) if zen.executions.exists() else 0,
                'slowest_execution': zen.executions.order_by('-execution_time_in_ms').first(),
                'last_execution': zen.executions.order_by('-executed_at').first(),
                'errors': zen.executions.filter(state=Execution.State.INVALID)
            }
        )

        return Response(response_data.data)
