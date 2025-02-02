# pylint: skip-file

"""
Tests for QueryZen client API.
"""

import pytest

from queryzen import Zen, DEFAULT_COLLECTION
from queryzen.backend import QueryZenResponse
from queryzen.exceptions import UncaughtBackendError, ZenDoesNotExist


def check_zen(zen: Zen, name, query, version):
    assert isinstance(zen, Zen)
    assert zen.query == query
    assert zen.name == name
    assert zen.version == version


def test_queryzen_create(queryzen):
    query = 'select * from mountain where :height > 10'
    name = 'mountain_view'

    q = queryzen.create(name, query=query)
    check_zen(q, name, query, 1)

    q = queryzen.create(name, query=query)
    check_zen(q, name, query, 2)


def test_queryzen_create_same_collection(queryzen):
    # Different collections should not raise anything.
    queryzen.create('mountain_view', collection='m', query='q')
    queryzen.create('mountain_view', collection='m', query='q')
    queryzen.create('mountain_view', collection='a', query='q')


def test_queryzen_default_collection(queryzen):
    q = queryzen.create(name='q', query='query')
    assert q.collection == DEFAULT_COLLECTION


def test_queryzen_get_one(queryzen):
    """
    Test that we get one query zen.
    """
    name = 'mountain_view'
    query = 'select 1'
    queryzen.create(name, query=query)

    q = queryzen.get(name=name)
    check_zen(q, name, version=1, query=query)

def test_uncaught_api_error_is_reported(queryzen):
    # All defined API error, like 409 for a Zen that already exists are handled
    # by the client, if any uncaught one shows up, we raise it.
    queryzen._client.create = lambda **_: QueryZenResponse(error='somerror', error_code=-1)
    queryzen._client.list = lambda **_: QueryZenResponse(error='somerror', error_code=-1)
    queryzen._client.get = lambda **_: QueryZenResponse(error='somerror', error_code=-1,
                                                        data=[1])
    queryzen._client.delete = lambda **_: QueryZenResponse(error='somerror', error_code=-1)
    queryzen._client.list = lambda **_: QueryZenResponse(error='somerror', error_code=-1)

    with pytest.raises(UncaughtBackendError):
        queryzen.create('s', 's')

    with pytest.raises(UncaughtBackendError):
        queryzen.get('s')

    with pytest.raises(UncaughtBackendError):
        queryzen.get_or_create('a', 'b')
    # Delete is not implemented
    # with pytest.raises(UnknownError):
    #     queryzen.delete('s', 's')

    with pytest.raises(UncaughtBackendError):
        queryzen.list()


def test_queryzen_get_one_unknown(queryzen):
    """
    Test that if we request a Zen, and it does not exist, an exception is raised.
    """

    with pytest.raises(ZenDoesNotExist):
        queryzen.get(name='qz_that_doesnt_exist')


def test_queryzen_get_or_create(queryzen):
    """
    Test QueryZen.get_or_create method.
    """
    name = 'zen'
    query = 'q'
    version = 1

    # Zen should not exist at this point.
    created, zen = queryzen.get_or_create(name=name, query=query)

    assert isinstance(created, bool)
    assert created is True
    check_zen(zen, name, query, version)

    # Zen should now exist as it was created before.
    created, zen = queryzen.get_or_create(name=name, query=query)

    assert isinstance(created, bool)
    assert created is False
    check_zen(zen, name, query, version)


def test_queryzen_list(queryzen):
    """
    Test queryzen.list
    """

    qs = queryzen.list()
    assert not qs  # Is empty

    q = queryzen.create('z', 'select 1')
    queryzen.create('z', 'select 2')

    qs = queryzen.list()

    assert len(qs) == 2
    assert isinstance(qs, list)
    assert qs[0].version == 1
    assert q == qs[0]
    assert qs[1].version == 2



def test_queryzen_filters(queryzen):
    qz = queryzen
    name = 'name1'
    collection = 'col1'
    version = 1
    qz.create(name, query='q', collection=collection)
    qz.create(name, query='q', collection=collection)
    qz.create('name2', query='q')

    result: list[Zen] = qz.list(name=name)

    assert all(
        map(lambda z: z.name == name, result)
    )

    assert all(
        map(lambda z: z.collection == collection, result)
    )

    assert not all(
        map(lambda z: z.version == version, result)
    )

    result: list[Zen] = qz.list(version=version)

    assert all(
        map(lambda z: z.version == version, result)
    )

    assert not all(
        map(lambda z: z.name == name, result)
    )

    assert not all(
        map(lambda z: z.collection == collection, result)
    )
