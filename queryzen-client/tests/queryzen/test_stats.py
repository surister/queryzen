import pytest

from queryzen import exceptions


def test_get_stats_without_executions_return_none(queryzen):
    """
    Test that if we try to get stats from a zen that does not have executions, stats return all fields None
    """
    name = 'mountain_view'
    query = 'select 1'
    q = queryzen.create(name, query=query)

    stats = queryzen.stats(name=q.name)
    assert all(value is None for value in stats.to_dict().values())


def test_get_stats_from_unknown(queryzen):
    """
    Test that if we try to get stats from an unknown queryzen, an exception is raised
    """
    with pytest.raises(exceptions.ZenDoesNotExistError):
        queryzen.stats(name='testing')


def test_get_stats(queryzen):
    """
    Test that if we request stats from a queryzen with executions it will return metrics
    """

    q = queryzen.create('t', 'select 1,2,3,4')

    for _ in range(5):
        queryzen.run(q)

    stats = queryzen.stats(name=q.name)

    assert all(value is not None for value in stats.to_dict().values())
