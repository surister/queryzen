import pytest

from queryzen import exceptions, Zen


def test_zen_delete(queryzen):
    name = 't'
    query = 'q'

    with pytest.raises(exceptions.ZenDoesNotExistError):
        queryzen.delete(Zen.empty())

    created, zen = queryzen.get_or_create(name, query)
    assert created and zen

    queryzen.delete(zen)

    with pytest.raises(exceptions.ZenDoesNotExistError):
        queryzen.get(name)
