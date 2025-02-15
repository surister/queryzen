from collections import OrderedDict

import pytest

from queryzen import exceptions
from queryzen.queryzen import ZenExecution


def test_run_basic(queryzen):
    """
    Check that we can run two sequential zens.
    """
    _, zen = queryzen.get_or_create('t', query='SELECT 1')

    queryzen.run(zen)
    assert len(zen.executions) == 1

    queryzen.run(zen)
    assert len(zen.executions) == 2


def test_run_executions(queryzen):
    """
    Test the properties of executions when running queries.
    """
    _, zen = queryzen.get_or_create('t', query='SELECT 1')
    assert len(zen.executions) == 0

    execution = queryzen.run(zen)

    assert len(zen.executions) == 1
    assert execution == zen.executions[0]
    assert not execution.error
    assert execution.rows
    assert execution.has_data()
    assert not execution.is_error

    zen = queryzen.get('t')

    # Right now we don't cache results so executions.rows and execution.columns are empty from api
    # but the rest should be identical.
    execution.rows = []
    execution.columns = []
    print(zen.executions[0])
    print(execution)
    assert zen.executions[0] == execution


def test_run_non_existing_zen(queryzen):
    """Try to run a Zen that does not exist."""
    _, zen = queryzen.get_or_create('t', query='SELECT 1')
    queryzen.delete(zen)

    with pytest.raises(exceptions.ZenDoesNotExistError):
        queryzen.run(zen)


def test_run_incorrect_query(queryzen):
    _, zen = queryzen.get_or_create('t', query='SELECT 1 + 2')

    # Sanity check, correct values are gotten.
    result = queryzen.run(zen)
    assert len(result.rows)
    assert result.rows[0][0] == 3

    zen = queryzen.create('t', query='SELECT t')
    result = queryzen.run(zen)
    assert result.error
    assert result.as_table() == """+-------------------+
| error             |
+-------------------+
| no such column: t |
+-------------------+"""


def test_zen_run_many(queryzen):
    _, zen = queryzen.get_or_create('t', query='SELECT 1')

    result = queryzen.run(zen)
    assert len(zen.executions) == 1

    assert isinstance(result, ZenExecution)
    assert not result.error
    assert result == zen.executions[0]

    n_times = 10
    for _ in range(n_times):
        queryzen.run(zen)

    assert len(zen.executions) == n_times + 1


def test_run_parameters(queryzen):
    query = """
    SELECT *
    FROM (VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie'))
    WHERE column2 LIKE :startswith OR column1 = :id;
    """
    _, zen = queryzen.get_or_create('t', query=query)

    result = queryzen.run(zen, id=2, startswith='A%')

    assert result.rows == [[1, 'Alice'], [2, 'Bob']]
    assert result.columns == ['column1', 'column2']


def test_run_query_databases(queryzen):
    zen = queryzen.create('t', 'select 1')

    queryzen.run(zen)  # Should not fail (if default is configured in the database)
    queryzen.run(zen, database='default')
    with pytest.raises(exceptions.DatabaseDoesNotExistError):
        queryzen.run(zen, database="DB_THAT_DOES_NOT_EXIST_12312312")


def test_run_query(queryzen):
    query = "SELECT * FROM (VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie')) as t WHERE column2 LIKE :startswith OR column1 = :id;"
    _, zen = queryzen.get_or_create('t', query=query)

    result = queryzen.run(zen, id=2, startswith='A%')
    assert result.rows == [[1, 'Alice'], [2, 'Bob']]
    assert result.columns == ['column1', 'column2']
    assert result.query == "SELECT * FROM (VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie')) as t WHERE column2 LIKE 'A%' OR column1 = 2;"


def test_run_bad_parameters(queryzen):
    """Test that if user tries to execute a query with
    parameters that are unknown
    """
    query = 'select * from mountain where height > :height AND country = :country'
    name = 'mountain_view'

    q = queryzen.create(name, query=query)

    with pytest.raises(exceptions.MissingParametersError):
        queryzen.run(q)

    with pytest.raises(exceptions.ParametersMissmatchError):
        queryzen.run(q, bad_parameter=1)


def test_missing_parameters(queryzen):
    """Query has two parameters but only one in default"""
    zen = queryzen.create(collection='m1',
                          name='mountain_view',
                          query='select (1 + :val - :val2) as r',
                          default={'val2': 1})

    with pytest.raises(exceptions.MissingParametersError):
        queryzen.run(zen)


def test_missing_parameters(queryzen):
    """Parameter that is not in the query is sent"""
    zen = queryzen.create(collection='m1',
                          name='mountain_view',
                          query='select (1 + :val - :val2) as r',
                          default={'val2': 1})

    with pytest.raises(exceptions.ParametersMissmatchError):
        queryzen.run(zen, strange_parameter=False)


def test_use_defaults(queryzen):
    """Query has two parameters but only one in default"""
    zen = queryzen.create(collection='m1',
                          name='mountain_view',
                          query='select (1 + :val1 - :val2) as r',
                          default={'val2': 1, 'val1': 2})
    default_params = {'val2': 1, 'val1': 2}

    # Use only defaults.
    result = queryzen.run(zen)
    assert result.rows[0][0] == 2
    assert OrderedDict(**result.parameters) == OrderedDict(**default_params)
    assert result.query == 'select (1 + 2 - 1) as r'

    # Use partial only one default and one param.
    result = queryzen.run(zen, val2=5)
    assert result.rows[0][0] == -2

    # Use two params.
    result = queryzen.run(zen, val1=29, val2=5)
    assert result.rows[0][0] == 25

def test_zen_sets_state_after_run(queryzen):
    """Test that after running a Zen, the state is correctly updated"""

    zen = queryzen.create('t', 'select 1/:val')
    assert zen.state == 'UN'

    queryzen.run(zen, val=1)
    assert zen.state == 'VA'

    zen = queryzen.create('t', 'select 1/')
    queryzen.run(zen)
    assert zen.state == 'IN'

def test_zen_several_queries(queryzen):
    """Test that multiple queries in sequence work.

    Also test that data is properly assigned to the responses in the API.
    """
    queries = [
        'create table if not exists t (a vachar)',
        "insert into t values ('one')",
    ]

    for query in queries:
        q = queryzen.create('t', query=query)
        r = queryzen.run(q)
        assert not r.is_error

    q = queryzen.create('t', 'select * from t')
    r = queryzen.run(q)
    assert r.rows[0][0] == 'one'

def test_other_database(queryzen):
    """Test other database than default"""
    q = queryzen.create('t', "select country, mountain, height from sys.summits where mountain = :mountain")
    r = queryzen.run(q, mountain='Mont Blanc', database='crate')
    assert r.rows[0][2] == 4808
