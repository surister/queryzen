# pylint: disable=C0114
import datetime
import json
import logging

from celery import shared_task

from django.conf import settings
from django.shortcuts import get_object_or_404

from apps.core.models import Zen, Execution
from apps.core.serializers import ZenExecutionResponseSerializer
from databases.base import Database

logger = logging.getLogger(__name__)


@shared_task
def run_query(database: str, pk: str, parameters: dict | None = None):
    executed_at = datetime.datetime.now(datetime.UTC)
    zen = get_object_or_404(Zen, pk=pk)
    execution = Execution(zen=zen)
    db_instance: Database = getattr(settings, 'ZEN_DATABASES').get(database)

    columns = rows = []
    query = ''
    try:
        columns, rows, query = db_instance.execute(zen.query, parameters)
        execution.state = Execution.State.VALID
        execution.row_count = len(rows)
        zen.state = Zen.State.VALID
    except Exception as e:  # pylint: disable=W0718
        execution.error = str(e)
        execution.row_count = 0
        execution.state = Execution.State.INVALID
        zen.state = Zen.State.INVALID

    execution.query = query
    execution.parameters = json.dumps(parameters)
    finished_at = datetime.datetime.now(datetime.UTC)

    execution_time = (finished_at - executed_at).total_seconds() * 1000  # milliseconds
    execution.finished_at = finished_at
    execution.total_time = execution_time
    execution.rows = rows
    execution.columns = columns

    zen.save()
    execution.save()
    print(ZenExecutionResponseSerializer(execution).data)
    return ZenExecutionResponseSerializer(execution).data
