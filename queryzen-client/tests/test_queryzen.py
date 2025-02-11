# pylint: skip-file

"""
Tests for QueryZen client API.
"""

import pytest

from queryzen import Zen
from queryzen.backend import QueryZenResponse
from queryzen import exceptions


def test_uncaught_api_error_is_reported(queryzen):
    """Test that API errors from the main methods that are not caught, are re-raised with
     UncaughtBackendError which is a special error that gives extra context and
     tells the user to report the error in Github."""
    error = QueryZenResponse(error='somerror', error_code=-1, data=[1])
    queryzen._client.create = lambda **_: error
    queryzen._client.filter = lambda **_: error
    queryzen._client.get = lambda **_: error
    queryzen._client.delete = lambda _: error
    queryzen._client.run = lambda **_: error

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

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.run(Zen.empty())

    error.data = []
    error.error = ''
    error.error_code = None
    queryzen._client.run = lambda **_: error

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.run(Zen.empty())
