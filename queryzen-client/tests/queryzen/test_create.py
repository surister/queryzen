import pytest

from queryzen import exceptions, DEFAULT_COLLECTION, Default
from tests.shared import check_zen


def test_create_simple(queryzen):
    query = 'select * from mountain where :height > 10'
    name = 'mountain_view'

    q = queryzen.create(name, query=query)
    check_zen(q, name, query, 1)

    q = queryzen.create(name, query=query)
    check_zen(q, name, query, 2)


def test_create_version(queryzen):
    """Test different combinations of version and auto"""
    query = 'select 1'
    name = 'mountain_views'

    queryzen.create(name, query=query, version=1)

    with pytest.raises(exceptions.ZenAlreadyExistsError):
        queryzen.create(name, query=query, version=1)

    queryzen.create(name, query=query, version=3)
    queryzen.create(name, query=query, version=4)

    zen = queryzen.create(name, query=query)
    assert zen.version == 5


def test_create_same_collection(queryzen):
    # Different collections should not raise anything.
    queryzen.create('mountain_view', collection='m', query='q')
    queryzen.create('mountain_view', collection='m', query='q')
    queryzen.create('mountain_view', collection='a', query='q')


def test_default_collection(queryzen):
    q = queryzen.create(name='q', query='query')
    assert q.collection == DEFAULT_COLLECTION


def test_extra_default(queryzen):
    """Test default values are in the query"""
    with pytest.raises(exceptions.DefaultValueDoesNotExistError):
        queryzen.create(collection='m1',
                        name='mountain_view1',
                        query='select1 (1 + :val - :val2) as r',
                        default={'val': 1, 'paquito': 2344})
        queryzen.create(collection='m1',
                        name='mountain_view1',
                        query='select1 (1 + :val - :val2) as r',
                        default=Default(val=1, two=2))

    queryzen.create(collection='m1',
                    name='mountain_view1',
                    query='select1 (1 + :val - :val2) as r',
                    default=Default(val=1, val2=2))


def test_bad_default_type(queryzen):
    """Default has to be either dict or Default"""
    with pytest.raises(ValueError):
        queryzen.create('t', query='t', default=1)
