# pylint: disable=C0114
import logging
import re

from django.conf import settings
from django.shortcuts import get_object_or_404

from django_filters import rest_framework as filters

from rest_framework.response import Response
from rest_framework import mixins, viewsets, status, views

from apps.core.exceptions import (ZenAlreadyExistsError,
                                  ExecutionEngineError,
                                  DatabaseDoesNotExistError,
                                  ZenDoesNotExistError,
                                  MissingParametersError)
from apps.core.filters import QueryZenFilter
from apps.core.models import Zen
from apps.core.serializers import (ZenSerializer,
                                   CreateZenSerializer,
                                   ExecuteZenSerializer, StatisticsSerializer)
from apps.core.tasks import run_query


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
        """Validates that the required parameters to run the query are given by the user
        or present in `default_parameters`

        Regex explanation:
        (:) -> Search character :
        (w+) -> Catch one or more letters, numbers... what is the param name
        """
        required_parameters = re.findall(r':(\w+)', zen.query)

        missing_parameters = []

        default_parameters_names = list(map(lambda k: k.get('name'), zen.default_parameters))
        for param in required_parameters:
            if param not in parameters and param not in default_parameters_names:
                missing_parameters.append(param)

        if missing_parameters:
            raise MissingParametersError(f'The Zen requires parameters'
                                         f' that were not supplied: {missing_parameters!r}')

    def get(self, request, collection: str, name: str, version: str):  # pylint: disable=W0613
        """Get a Zen."""
        queryset = Zen.filter_by(collection=collection,
                                 name=name,
                                 version=version)

        obj = queryset.first()

        if not obj:
            raise ZenDoesNotExistError()

        return Response(ZenSerializer(obj, many=False).data)

    def post(self, request, collection, name, version):
        """Runs a Zen in the backend."""
        serializer = ExecuteZenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        zen = get_object_or_404(Zen,
                                collection=collection,
                                name=name,
                                version=version)

        # Parameters to be passed to the task.
        parameters = zen.get_parameters(serializer.validated_data['parameters'])
        zen.validate_parameters(parameters)

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
                                        parameters)
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


class StatisticsView(views.APIView):
    """View to retrieve statistical execution time metrics for a given Zen version."""

    def get(self, request, collection: str, name: str, version: str):  # pylint: disable=W0613
        """
        Get statistics from a Zen version.

        Available statistics:
        - min_execution_time_in_ms
        - max_execution_time_in_ms
        - mean_execution_time_in_ms
        - mode_execution_time_in_ms
        - median_execution_time_in_ms
        - variance
        - standard_deviation
        - range
        """

        queryset = Zen.filter_by(collection=collection,
                                 name=name,
                                 version=version)

        obj: Zen | None = queryset.first()
        if not obj:
            raise ZenDoesNotExistError()

        if not obj.executions.count():
            metrics = StatisticsSerializer(
                {
                    'min_execution_time_in_ms': None,
                    'max_execution_time_in_ms': None,
                    'mean_execution_time_in_ms': None,
                    'mode_execution_time_in_ms': None,
                    'median_execution_time_in_ms': None,
                    'variance': None,
                    'standard_deviation': None,
                    'range': None,
                }
            )
        else:
            executions = obj.executions.order_by('total_time')

            metrics = StatisticsSerializer(
                {
                    'min_execution_time_in_ms': executions.first().total_time,
                    'max_execution_time_in_ms': executions.last().total_time,
                    'mean_execution_time_in_ms': obj.mean_execution_time_in_ms,
                    'mode_execution_time_in_ms': obj.mode_execution_time_in_ms,
                    'median_execution_time_in_ms': obj.median_execution_time_in_ms,
                    'variance': obj.variance,
                    'standard_deviation': obj.standard_deviation,
                    'range': executions.last().total_time - executions.first().total_time,
                }
            )

        return Response(metrics.data, status=status.HTTP_200_OK)
