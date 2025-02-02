# pylint: skip-file

import datetime

from queryzen import DEFAULT_COLLECTION
from queryzen import Zen


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
               created_at=t
               ).to_dict() == {'collection': 'main',
                               'created_at': t,
                               'created_by': 'not_implemented',
                               'description': '-1',
                               'executions': [],
                               'id': -1,
                               'name': '_',
                               'query': '_',
                               'state': 'unknown',
                               'version': -1}
