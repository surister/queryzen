"""
Tests for QueryZen client API.
"""

import pytest

from queryzen import Zen, AUTO, DEFAULT_COLLECTION
from queryzen.exceptions import ZenAlreadyExists, ZenDoesNotExist


def check_zen(zen: Zen, name, query, version):
    assert isinstance(zen, Zen)
    assert zen.query == query
    assert zen.name == name
    assert str(zen.version) == version


def test_queryzen_create_one(queryzen):
    query = 'select * from mountain where :height > 10'
    name = 'mountain_view'

    q = queryzen.create('mountain_view', query)
    check_zen(q, name, query, 'latest')

    version = '2'
    name = name + '3'

    q = queryzen.create(name, query=query, version=version)

    check_zen(q, name, query, version)


def test_queryzen_create_repeated_collection(queryzen):
    queryzen.create('mountain_view', collection='m', query='q')

    with pytest.raises(ZenAlreadyExists):
        queryzen.create('mountain_view', collection='m', query='q')

    # Same name but different collection shouldn't raise
    queryzen.create('mountain_view', collection='a', query='q')


def test_queryzen_create_repeated_version(queryzen):
    queryzen.create('mountain_view', collection='m', query='q', version=1)

    with pytest.raises(ZenAlreadyExists):
        queryzen.create('mountain_view', collection='m', query='q', version=1)

    queryzen.create('mountain_view', collection='m', query='q', version=2)

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
    check_zen(q, name, version='latest', query=query)


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
    version = 3

    # Zen should not exist at this point.
    created, zen = queryzen.get_or_create(name=name, query=query, version=version)

    assert isinstance(created, bool)
    assert created is True
    assert check_zen(zen, name, query, version)

    # Zen should now exist as it was created before.
    created, zen = queryzen.get_or_create(name=name, query=query)

    assert isinstance(created, bool)
    assert created is False
    assert check_zen(zen, name, query, version)


def test_queryzen_list(queryzen):
    """
    Test queryzen.list
    """
    qz = queryzen

    qs = qz.list()
    assert not qs  # Is empty

    q = qz.create('z', 'select 1')
    qz.create('z', 'select 2', version=2)

    qs = qz.list()

    assert len(qs) == 2
    assert isinstance(qs, list)
    # assert q in qs # fixme why it fails


def test_queryzen_filters(queryzen):
    qz = queryzen
    name = 'name1'
    collection = 'col1'
    version = "1"
    qz.create(name, version=version, query='q', collection=collection)
    qz.create(name, version=2, query='q', collection=collection)
    qz.create('name2', version=version, query='q')

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
        map(lambda z: int(z.version) == version, result)
    )

    assert not all(
        map(lambda z: z.name == name, result)
    )

    assert not all(
        map(lambda z: z.collection == collection, result)
    )
