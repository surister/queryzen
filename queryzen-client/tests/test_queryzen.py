# pylint: skip-file

"""
Tests for QueryZen client API.
"""

import pytest

from queryzen import Zen, DEFAULT_COLLECTION
from queryzen.backend import QueryZenResponse
from queryzen import exceptions
from queryzen.exceptions import ZenDoesNotExistError
from queryzen.queryzen import ZenExecution


def test_uncaught_api_error_is_reported(queryzen):
    """Test that API errors from the main methods that are not caught, are re-raised with
     UncaughtBackendError which is a special error that gives extra context and
     tells the user to report the error in Github."""
    queryzen._client.create = lambda **_: QueryZenResponse(error='somerror', error_code=-1)
    queryzen._client.filter = lambda **_: QueryZenResponse(error='somerror', error_code=-1)
    queryzen._client.get = lambda **_: QueryZenResponse(error='somerror', error_code=-1,
                                                        data=[1])
    queryzen._client.delete = lambda _: QueryZenResponse(error='somerror', error_code=-1)

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.create('s', 's')

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.get('s')

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.get_or_create('a', 'b')

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.delete(Zen.empty())

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.filter()
