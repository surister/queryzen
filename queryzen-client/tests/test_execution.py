import dataclasses
import datetime
import json
from collections.abc import Iterable

import pytest

from queryzen import Default
from queryzen.exceptions import ParametersMissmatchError
from queryzen.queryzen import ZenExecution


def test_execution_serialization():
    expected_dict = {'id': 'exec_123',
                     'row_count': 10,
                     'state': 'VA',
                     'started_at': datetime.datetime(2024, 2, 11, 12, 0),
                     'finished_at': datetime.datetime(2024, 2, 11, 12, 0, 5),
                     'total_time': 5000,
                     'query': 'SELECT * FROM users',
                     'error': '',
                     'parameters': {'limit': 100},
                     'rows': [['Alice', 30], ['Bob', 25]],
                     'columns': ['name', 'age']}

    zen_execution = ZenExecution(**expected_dict)
    zen_dict = zen_execution.to_dict()
    assert zen_dict == expected_dict


def test_execution_parameters():
    params = {"limit": 100}
    expected_dict = {'id': 'exec_123',
                     'row_count': 10,
                     'state': 'VA',
                     'started_at': datetime.datetime(2024, 2, 11, 12, 0),
                     'finished_at': datetime.datetime(2024, 2, 11, 12, 0, 5),
                     'total_time': 5000,
                     'query': 'SELECT * FROM users',
                     'error': '',
                     'parameters': json.dumps(params),
                     'rows': [['Alice', 30], ['Bob', 25]],
                     'columns': ['name', 'age']}

    zen_execution = ZenExecution(**expected_dict)

    with pytest.raises(ValueError):
        expected_dict['parameters'] = 'not a valid json'
        ZenExecution(**expected_dict)
    assert zen_execution.parameters == params


def test_execution(queryzen):
    """Test the result of a queryzen execution result"""
    q = queryzen.create('t', 'select 1,2,3,4')

    result = queryzen.run(q)

    assert isinstance(result, ZenExecution)
    assert isinstance(result.is_error, bool)
    assert not result.error
    assert isinstance(result.has_data(), bool)
    assert result.has_data()


def test_execution_row_at(queryzen):
    q = queryzen.create('t', """
    SELECT column1 as id, column2 as name, column3 as age FROM (
    VALUES
        (1, 'Alice Johnson', 28),
        (2, 'Bob Smith', 35),
        (3, 'Charlie Brown', 22)
    )
""")

    result = queryzen.run(q)
    assert not result.is_error
    assert result.row_at(0) == [1, 'Alice Johnson', 28]
    assert result.row_at(1) == [2, 'Bob Smith', 35]


def test_execution_iter_rows(queryzen):
    q = queryzen.create('t', """
        SELECT column1 as id, column2 as name, column3 as age FROM (
        VALUES
            (1, 'Alice Johnson', 28),
            (2, 'Bob Smith', 35),
            (3, 'Charlie Brown', 22)
        )
    """)

    result = queryzen.run(q)
    assert isinstance(result.iter_rows(), Iterable)
    assert list(result) == list(result.iter_rows()) == [[1, 'Alice Johnson', 28],
                                                        [2, 'Bob Smith', 35],
                                                        [3, 'Charlie Brown', 22]]


def test_execution_iter_cols(queryzen):
    q = queryzen.create('t', """
        SELECT column1 as id, column2 as name, column3 as age FROM (
        VALUES
            (1, 'Alice Johnson', 28),
            (2, 'Bob Smith', 35),
            (3, 'Charlie Brown', 22)
        )
    """)
    result = queryzen.run(q)
    assert isinstance(result.iter_cols(), Iterable)
    assert list(result.iter_cols()) == [[1, 2, 3],
                                        ['Alice Johnson', 'Bob Smith', 'Charlie Brown'],
                                        [28, 35, 22]]

def test_execution_parameters(queryzen):
    parameters = {
        'value': 1,
        'name': 'some'
    }
    q = queryzen.create('t',"select :value as :name")
    result = queryzen.run(q, **parameters)
    assert result.parameters == result.parameters

    # The locally previewed query has to be the same that was executed
    assert result.query == q.preview(**parameters)

def test_execution_parameter_raises(queryzen):
    """
    Test that when we try to run a Zen, without supplying the necessary parameters, it raises an
    Exception.
    """
    parameters = {
        'value': 1,
        'not_existing_parameter': 'some'
    }

    q = queryzen.create('t',"select :value as :name")

    with pytest.raises(ParametersMissmatchError):
        queryzen.run(q, **parameters)

def test_execution_parameter_defaults(queryzen):
    """
    Test that default parameters are respected.
    """
    default_parameters = {
        'value': 1
    }
    parameters = {
        'name': 'some'
    }

    q = queryzen.create('t', "select :value as :name", default=default_parameters)
    result = queryzen.run(q, **parameters)

    # Merge two parameters dictionary
    parameters.update(default_parameters)

    assert result.parameters == parameters

def test_execution_parameter_defaults_1(queryzen):
    """
    Test that default parameters are respected, using `Default` object.
    """
    default_parameters = Default(value=1)
    parameters = {
        'name': 'some'
    }

    q = queryzen.create('t', "select :value as :name", default=Default(value=1))
    result = queryzen.run(q, **parameters)

    # Merge the two parameters dictionary
    parameters.update(default_parameters.to_dict())

    assert result.parameters == parameters

def test_execution_factory(queryzen):

    @dataclasses.dataclass
    class Person:
        id: int
        name: str
        age: int

    q = queryzen.create('t', """
        SELECT column1 as id, column2 as name, column3 as age FROM (
        VALUES
            (1, 'Alice Johnson', 28),
            (2, 'Bob Smith', 35),
            (3, 'Charlie Brown', 22)
        )
    """)

    result = queryzen.run(q, factory=Person)

    assert len(result.rows) == 3
    assert isinstance(result.rows[0], Person)
    assert result.rows[0].id == 1
    assert result.rows[0].name == 'Alice Johnson'
    assert result.rows[0].age == 28
