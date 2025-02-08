# pylint: skip-file
import logging

import httpx
import pytest
import datetime

import requests

from queryzen import QueryZen, constants
from queryzen.backend import QueryZenResponse
from queryzen.queryzen import QueryZenClientABC, Zen


def filter_dataclasses(items: list, filters: dict[str, object]) -> list:
    return [item for item in items if all(getattr(item, k) == v for k, v in filters.items())]


class MockQueryZenBackendClient(QueryZenClientABC):
    # THIS CLASS IS VERY OUTDATED, DONT USE,
    def __init__(self):
        self.zens = []

    def create(self, name, version, query, collection) -> 'QueryZenResponse':
        new_zen = Zen(
            id=1,
            name=name,
            version=version,
            query=query,
            created_at=datetime.datetime.now(),
            collection=collection

        )
        self.zens.append(
            new_zen
        )

        return QueryZenResponse(
            error=None,
            started_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
            finished_at=datetime.datetime(2024, 1, 1, 12, 0, 2),
            execution_time=1.4,
            data=[
                new_zen.to_dict()
            ]
        )

    def delete(self) -> 'QueryZenResponse':
        return QueryZenResponse(
            error=None,
            started_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
            finished_at=datetime.datetime(2024, 1, 1, 12, 0, 2),
            execution_time=1.4,  # 30 minutes in seconds
            data=[]
        )

    def filter(self, **filters) -> 'QueryZenResponse':
        if not filters:
            print(list(map(lambda x: x.to_dict(), self.zens)))
            zens = list(map(lambda x: x.to_dict(), self.zens))
        else:
            zens = map(lambda x: x.to_dict(), filter_dataclasses(self.zens, filters))

        return QueryZenResponse(
            error=None,
            started_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
            finished_at=datetime.datetime(2024, 1, 1, 12, 0, 2),
            execution_time=1.4,  # 30 minutes in seconds
            data=zens
        )

    def get(self, name: str, version: str) -> 'QueryZenResponse':

        zen = list(
            map(
                lambda x: x.to_dict(),
                filter(
                    lambda z: z.name == name and z.version == version,
                    self.zens
                )
            )
        )

        return QueryZenResponse(
            error=None,
            started_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
            finished_at=datetime.datetime(2024, 1, 1, 12, 0, 2),
            execution_time=1.4,  # 30 minutes in seconds
            data=zen
        )

    def run(self) -> 'QueryZenResponse':
        return QueryZenResponse(
            error=None,
            started_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
            finished_at=datetime.datetime(2024, 1, 1, 12, 0, 2),
            execution_time=1.4,  # 30 minutes in seconds
            data=[]
        )


@pytest.fixture
def mocked_queryzen():
    qz = QueryZen(client=MockQueryZenBackendClient())
    return qz


@pytest.fixture
def local_queryzen():
    """This QueryZen client is intended to use with a real backend instance being run locally.

    It will refresh the database after every test run.
    """
    response = httpx.get(f'{constants.BACKEND_URL}/_testing/clean_db', timeout=1)
    assert response.status_code == 200

    qz = QueryZen()
    yield qz




@pytest.fixture
def queryzen(request) -> QueryZen:
    # We either use mocked_queryzen or local_queryzen depending on chosen setting.
    use_local = request.config.getoption("--use-local")  # Get a CLI option
    use_mocked = request.config.getoption("--use-mocked")
    queryzen = 'mocked_queryzen' if use_mocked else 'local_queryzen'
    print(f'💡💡💡 IMPORTANT: Using {queryzen} fixture')
    return request.getfixturevalue(queryzen)


def pytest_addoption(parser):
    parser.addoption("--use-local",
                     action="store_true",
                     help="Use local_queryzen instead of mocked_queryzen")
    parser.addoption("--use-mocked",
                     action="store_true",
                     help="Use mocked_queryzen instead of local_queryzen")
