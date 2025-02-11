import pytest

from queryzen import exceptions
from tests.shared import check_zen


def test_get_one(queryzen):
    """
    Test that we get one query zen.
    """
    name = 'mountain_view'
    query = 'select 1'
    queryzen.create(name, query=query)

    q = queryzen.get(name=name)
    check_zen(q, name, version=1, query=query)


def test_get_latest(queryzen):
    name = 'mountain_view'
    query = 'select 1'
    queryzen.create(name, query=query)
    queryzen.create(name, query=query)
    zen = queryzen.get(name=name)  # Does not raise exception (as we only return one), it was a bug.
    assert zen.version == 2


def test_get_parameter_validation(queryzen):
    with pytest.raises(ValueError):
        queryzen.get('n', version=None)
        queryzen.get('n', version='test')


def test_get_version(queryzen):
    name = 'mountain_view'
    queryzen.create(name, query='1')
    queryzen.create(name, query='2')
    queryzen.create(name, query='3')
    assert queryzen.get(name, version=1).query == '1'
    assert queryzen.get(name, version=2).query == '2'
    assert queryzen.get(name, version=3).query == '3'

def test_get_one_unknown(queryzen):
    """
    Test that if we request a Zen, and it does not exist, an exception is raised.
    """

    with pytest.raises(exceptions.ZenDoesNotExistError):
        queryzen.get(name='qz_that_doesnt_exist')


def test_get_or_create(queryzen):
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
