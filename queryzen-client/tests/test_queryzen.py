# pylint: skip-file

"""
Tests for QueryZen client API.
"""

import pytest

from queryzen import Zen, DEFAULT_COLLECTION
from queryzen.backend import QueryZenResponse
from queryzen import exceptions
from queryzen.queryzen import ZenExecution


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


def test_queryzen_create_version(queryzen):
    """Test different combinations of version and auto"""
    query = 'select 1'
    name = 'mountain_views'

    queryzen.create(name, query=query, version=1)

    with pytest.raises(exceptions.ZenAlreadyExists):
        queryzen.create(name, query=query, version=1)
    #
    queryzen.create(name, query=query, version=3)
    queryzen.create(name, query=query, version=4)

    zen = queryzen.create(name, query=query)
    assert zen.version == 5


def test_queryzen_create_same_collection(queryzen):
    # Different collections should not raise anything.
    queryzen.create('mountain_view', collection='m', query='q')
    queryzen.create('mountain_view', collection='m', query='q')
    queryzen.create('mountain_view', collection='a', query='q')


def test_queryzen_default_collection(queryzen):
    q = queryzen.create(name='q', query='query')
    assert q.collection == DEFAULT_COLLECTION


def test_uncaught_api_error_is_reported(queryzen):
    # All defined API error, like 409 for a Zen that already exists are handled
    # by the client, if any uncaught one shows up, we raise it.
    queryzen._client.create = lambda **_: QueryZenResponse(error='somerror', error_code=-1)
    queryzen._client.list = lambda **_: QueryZenResponse(error='somerror', error_code=-1)
    queryzen._client.get = lambda **_: QueryZenResponse(error='somerror', error_code=-1,
                                                        data=[1])
    queryzen._client.delete = lambda _: QueryZenResponse(error='somerror', error_code=-1)
    queryzen._client.list = lambda **_: QueryZenResponse(error='somerror', error_code=-1)

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.create('s', 's')

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.get('s')

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.get_or_create('a', 'b')

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.delete(Zen.empty())

    with pytest.raises(exceptions.UncaughtBackendError):
        queryzen.list()


def test_queryzen_get_one(queryzen):
    """
    Test that we get one query zen.
    """
    name = 'mountain_view'
    query = 'select 1'
    queryzen.create(name, query=query)

    q = queryzen.get(name=name)
    check_zen(q, name, version=1, query=query)


def test_queryzen_get_parameter_validation(queryzen):
    with pytest.raises(ValueError):
        queryzen.get('n', version=None)
        queryzen.get('n', version='test')


def test_queryzen_get_one_unknown(queryzen):
    """
    Test that if we request a Zen, and it does not exist, an exception is raised.
    """

    with pytest.raises(exceptions.ZenDoesNotExistError):
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


def test_queryzen_list_filters(queryzen):
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


def test_zen_delete(queryzen):
    name = 't'
    query = 'q'

    with pytest.raises(exceptions.ZenDoesNotExistError):
        # Make sure it does not exist
        queryzen.get(name)

    created, zen = queryzen.get_or_create(name, query)
    assert created and zen

    deleted = queryzen.delete(zen)
    assert deleted

    with pytest.raises(exceptions.ZenDoesNotExistError):
        queryzen.get(name)


def test_zen_run_basic(queryzen):
    """
    Check that we can run two sequential zens.
    """
    _, zen = queryzen.get_or_create('t', query='SELECT 1')

    queryzen.run(zen, database='testing')
    assert len(zen.executions) == 1

    queryzen.run(zen, database='testing')
    assert len(zen.executions) == 2


def test_zen_run_non_existing_zen(queryzen):
    _, zen = queryzen.get_or_create('t', query='SELECT 1')
    queryzen.run(zen, database='testing')
    # _, zen = queryzen.get_or_create('t', query='SELECT 1')


def test_zen_run(queryzen):
    _, zen = queryzen.get_or_create('t', query='SELECT 1')

    result = queryzen.run(zen, database='testing')
    assert len(zen.executions) == 1

    assert isinstance(result, ZenExecution)
    assert not result.error
    assert result == zen.executions[0]

    n_times = 10
    for _ in range(n_times):
        queryzen.run(zen, database='testing')

    assert len(zen.executions) == n_times + 1


def test_zen_run_parameters(queryzen):
    query = """
    SELECT *
    FROM (VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie'))
    WHERE column2 LIKE :startswith OR column1 = :id;
    """
    _, zen = queryzen.get_or_create('t', query=query)

    result = queryzen.run(zen, database='testing', id=2, startswith='A%')

    assert result.rows == [[1, 'Alice'], [2, 'Bob']]
    assert result.columns == ['column1', 'column2']


def test_zen_run_query(queryzen):
    # THIS TEST DEPENDS ON A database that implements `GET COMPILED QUERY`.
    # For example CrateDB.
    query = "SELECT * FROM (VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie')) as t WHERE col2 LIKE :startswith OR col1 = :id;"
    _, zen = queryzen.get_or_create('t', query=query)

    result = queryzen.run(zen, database='crate', id=2, startswith='A%')

    assert result.rows == [[1, 'Alice'], [2, 'Bob']]
    assert result.columns == ['col1', 'col2']
    assert result.query == "SELECT * FROM (VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie')) as t WHERE col2 LIKE 'A%' OR col1 = 2;"


# todo handle if database does not exist or there is no configured database
# handle if parameters are not being sent
# handle if query is raises error (wrong syntax) - or rather that database fails.


def test_run_query_not_passing_required_params_raise_exception(queryzen):
    """
    Test that if user tries to execute a query with params and no params are found, the API raises an exception.
    """
    query = 'select * from mountain where height > :height AND country = :country'
    name = 'mountain_view'

    q = queryzen.create(name, query=query)

    with pytest.raises(exceptions.MissingParametersException):
        queryzen.run(q, database='crate')

    with pytest.raises(exceptions.MissingParametersException):
        queryzen.run(q, database='crate', **{'bad_parameter': 1})
