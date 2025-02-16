"""
Code for the backend ABC class and HTTP implementation, if you implement QueryZen in other protocol
you would use classes in this file to make a new Client-Api for that new implementation.

Implement QueryZenClientABC to make a new client.
"""
import abc
import dataclasses
import datetime
import typing
import urllib
from typing import Any

import httpx

from . import constants
from .constants import DEFAULT_COLLECTION
from .types import _AUTO, AUTO, Default


class Url(str):
    """
    Represents an URL.
    """

    def __truediv__(self, other):
        return Url(
            self +
            f'{'/' if not self.endswith('/') else ''}' +
            str(other)
        )


@dataclasses.dataclass
class QueryZenResponse:
    """Represents a response from the backend"""
    error_code: int | None = None
    error: str | None = None
    started_at: datetime.datetime = None
    finished_at: datetime.datetime = None
    execution_time: float = None  # The execution time of the query in milliseconds.
    data: list[dict] = dataclasses.field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Returns whether the action resulted in an error."""
        return not self.error

    def get_from_data(self, key) -> Any:
        return self.data[0].get(key)


class QueryZenClientABC(abc.ABC):
    """Abstract class for a QueryZen client."""

    @abc.abstractmethod
    def make_response(self, response) -> QueryZenResponse:
        """Abc method to map the response from the client to the response class ``QueryZenResponse``
        """

    @abc.abstractmethod
    def create(self,
               *,
               collection,
               name,
               version,
               description,
               query,
               default: Default | dict[str: typing.Any]) -> QueryZenResponse:
        """Abc method to create one ``Zen``"""

    @abc.abstractmethod
    def get(self,
            collection: str,
            name: str,
            version: str) -> QueryZenResponse:
        """Abc method to get a ``Zen``"""

    @abc.abstractmethod
    def filter(self, **filters) -> QueryZenResponse:
        """Abc method to get all ``Zen`` and filter them by ``filters``"""

    @abc.abstractmethod
    def delete(self,
               zen: 'Zen') -> QueryZenResponse:
        """Abc method for deleting a ``Zen``"""

    @abc.abstractmethod
    def run(self,
            name: str,
            version: int,
            database: str,
            timeout: int,
            collection: str = DEFAULT_COLLECTION,
            **parameters: dict) -> QueryZenResponse:
        """Abc method for running a ``Zen``"""


class QueryZenHttpClient(QueryZenClientABC):
    """
    QueryZen HTTP implementation, the default implementation and implemented by QueryZen.

    This class handles the management of ``Zen``s in sync with the HTTP backend developed by us.

    It uses httpx to make the http requests.
    """
    MAIN_ENDPOINT = 'zen/'
    COLLECTIONS = 'collection/'
    VERSION = 'version/'

    def __init__(self, client: httpx.Client = None):
        self.client: httpx.Client = (client
                                     or httpx.Client(timeout=int(constants.DEFAULT_HTTP_TIMEOUT)))
        self.url: Url = Url(constants.BACKEND_URL or constants.LOCAL_URL)

    def make_url(self, collection: str, name: str, version: str) -> str:
        # todo make test
        """Creates a valid QueryZen REST url

        Args:
            collection: The collection
            name: The name
            version: The name

        Returns:
            A fqdn that is valid to run HTTP requests against.
        """
        return (self.url /
                self.COLLECTIONS /
                collection /
                self.MAIN_ENDPOINT /
                name /
                self.VERSION /
                version /
                '')

    def make_response(self, response: httpx.Response) -> QueryZenResponse:
        """
        Httpx implementation of `make_response`, error in details like {'detail': 'error'} are
        flattened out, if several errors are returned we will lose them.

        assigned `error_code`s are HTTP error codes.
        """
        z_response = QueryZenResponse()
        resp_data = response.json()

        # Error handling.
        if not response.is_success:
            z_response.error_code = response.status_code

            # If api response with {'detail': 'error'} we unwrap it to have flat messages.
            z_response.error = resp_data.get('detail') if 'detail' in resp_data else response.text

        # Make it always a list
        z_response.data = resp_data if isinstance(resp_data, list) else [resp_data]
        return z_response

    def create(self,
               *,
               name: str,
               collection: str = DEFAULT_COLLECTION,
               version: _AUTO = AUTO,
               description: str = '',
               query: str,
               default: 'Default') -> QueryZenResponse:
        """Creates a ``Zen`` via PUT request to the backend.

        The version is automatically handled by QueryZen, it is an integer that is auto-incremented
        e.g. 1, 2, 3

        Args:
            name: The name of the ``Zen``
            version: The version of the Zen, integer, by default it will be the last version + 1
            collection: The name of the collection, default is ``DEFAULT_COLLECTION``
            description: The description of the ``Zen``
            query: The query of the ``Zen``
            default: The default values to be sent, always a dict of {name: value}
        """

        payload = {
            'description': description,
            'query': query,
        }
        if default:
            payload['default_parameters'] = default.to_dict()

        response = self.client.put(
            self.make_url(collection, name, version),
            json=payload
        )
        return self.make_response(response)

    def filter(self, **filters) -> QueryZenResponse:
        response = httpx.get(self.url / self.MAIN_ENDPOINT / '?' + urllib.parse.urlencode(filters))
        return self.make_response(response)

    def get(self,
            collection: str,
            name: str,
            version: str) -> QueryZenResponse:
        response = self.client.get(self.make_url(collection, name, version))
        return self.make_response(response)

    def delete(self, zen: 'Zen') -> QueryZenResponse:
        response = self.client.delete(self.make_url(zen.collection, zen.name, zen.version))
        return self.make_response(response)

    def run(self,
            name: str,
            version: int,
            database: str = None,
            timeout: int = None,
            collection: str = DEFAULT_COLLECTION,
            parameters: dict = None) -> QueryZenResponse:
        response = self.client.post(self.make_url(collection, name, str(version)),
                                    json={'version': version,
                                          'timeout': timeout,
                                          'parameters': parameters,
                                          'database': database})
        return self.make_response(response)
