# pylint: skip-file
import datetime
import json

import pytest

from queryzen import DEFAULT_COLLECTION
from queryzen import Zen
from queryzen.queryzen import ZenExecution


def test_zen():
    # Properly instantiates.
    Zen(id=-1,
        name='_',
        version=-1,
        query='_',
        description='-1',
        created_at=datetime.datetime.now()
        )
    assert Zen.empty() == Zen.empty()


def test_zen_difference():
    assert not Zen.empty().difference(Zen.empty())

    zen = Zen.empty()
    zen.version = 1
    zen.name = 'd'
    assert list(Zen.empty().difference(zen).keys()) == ['name', 'version']

    difference = ['id', 'query']
    zen = Zen.empty()
    zen.id = '123'
    zen.query = '123'
    assert list(Zen.empty().difference(zen, difference).keys()) == difference

    with pytest.raises(TypeError):
        zen.difference({'id': 1}, compare=['id'])


def test_zen_defaults():
    zen = Zen(id=-1,
              name='_',
              version=-1,
              query='_',
              description='-1',
              created_at=datetime.datetime.now()
              )

    assert zen.collection == DEFAULT_COLLECTION


def test_zen_to_dict():
    t = datetime.datetime.now()
    assert Zen(id=-1,
               name='_',
               version=-1,
               query='_',
               description='-1',
               created_at=t).to_dict() == {'collection': 'main',
                                           'created_at': t,
                                           'created_by': 'not_implemented',
                                           'default_parameters': {},
                                           'description': '-1',
                                           'executions': [],
                                           'id': -1,
                                           'name': '_',
                                           'query': '_',
                                           'state': 'unknown',
                                           'version': -1}


def test_zen_preview():
    zen = Zen.empty()
    zen.query = 'SELECT * FROM system WHERE somedata > :intvalue OR uuid == :strvalue'
    expected = "SELECT * FROM system WHERE somedata > 123 OR uuid == 'adsfasdfasfasdfads'"
    assert zen.preview(intvalue=123, strvalue='adsfasdfasfasdfads') == expected


def test_zen_execution_serialization():
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
