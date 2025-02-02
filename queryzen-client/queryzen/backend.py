"""
Code for the backend ABC class and HTTP implementation, if you implement QueryZen in other protocol
you would use classes in this file to make a new Client-Api for that new implementation.

Implement QueryZenClientABC to make a new client.
"""
import abc
import dataclasses
import datetime
import os
import urllib

import httpx

from .constants import DEFAULT_COLLECTION
from .types import _AUTO


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
    """
    Response from the backend.
    """
    error_code: int | None = None
    error: str | None = None
    started_at: datetime.datetime = None
    finished_at: datetime.datetime = None
    execution_time: float = None
    data: list[dict] = dataclasses.field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Returns whether the action resulted in an error."""
        return not self.error

class QueryZenClientABC(abc.ABC):
    """
    Abstract class for a QueryZen client.
    """

    @abc.abstractmethod
    def create(self, *, name, version, collection, description, query) -> QueryZenResponse:
        """Create one ``Zen``"""


    @abc.abstractmethod
    def get(self, name: str, version: str) -> QueryZenResponse:
        """Get ``Zen``"""


    @abc.abstractmethod
    def list(self, **filters) -> list[QueryZenResponse]:
        """Get all ``Zen`` and filter them by ``filters``"""

    @abc.abstractmethod
    def delete(
            self,
            name: str,
            version: int,
            collection: str = DEFAULT_COLLECTION
    ) -> QueryZenResponse:
        """Abc method for deleting a ``Zen``"""

    @abc.abstractmethod
    def run(
            self,
            name: str,
            version: int,
            collection: str = DEFAULT_COLLECTION
    ) -> QueryZenResponse:
        """Run a ``Zen``"""

class QueryZenHttpClient(QueryZenClientABC):
    """
    QueryZen HTTP implementation, the default implementation and implemented by QueryZen.

    This class handles the management of ``Zen``s in sync with the HTTP backend developed by us.

    It uses httpx to make the http requests.
    """
    MAIN_ENDPOINT = 'zen/'
    COLLECTIONS = 'collections/'

    def __init__(self, client: httpx.Client = None):
        self.client: httpx.Client = client or httpx.Client()
        self.url: Url = Url(
            os.getenv('API_URL') or 'http://localhost:8000'
        )

    def create(self,
               *,
               name: str,
               version: int | _AUTO,
               collection: str = DEFAULT_COLLECTION,
               description: str = '',
               query: str,
               ) -> QueryZenResponse:
        """
        Creates a ``Zen`` via PUT request to the backend.

        Args:
            name: The name of the ``Zen``
            version: The version of the ``Zen``
            collection: The name of the collection, default is ``DEFAULT_COLLECTION``
            description: The description of the ``Zen``
            query: The query of the ``Zen``
        """
        z_response = QueryZenResponse()

        response = self.client.put(
            self.url / self.COLLECTIONS / collection / self.MAIN_ENDPOINT / name + '/',
            json={
                'description': description,
                'query': query,
                'version': str(version)
            }
        )

        resp_data = response.json()

        # Error handling.
        if not response.is_success:
            z_response.error_code = response.status_code

            # If api response with {'detail': 'error'} we unwrap it to have nicer messages
            z_response.error = resp_data.get(
                'detail') if 'detail' in resp_data else resp_data

        # Make it always in a list
        z_response.data = resp_data if isinstance(resp_data, list) else [resp_data]
        return z_response

    def list(self, **filters) -> QueryZenResponse:
        z_response = QueryZenResponse()

        response = httpx.get(
            self.url / self.MAIN_ENDPOINT / '?' + urllib.parse.urlencode(filters)
        )

        if response.is_error:
            z_response.error = response.text
        z_response.data = response.json()

        return z_response

    def get(self,
            name: str,
            version: int,
            collection: str = DEFAULT_COLLECTION
            ) -> QueryZenResponse:
        z_response = QueryZenResponse()

        response = self.client.get(
            self.url / self.COLLECTIONS / collection / self.MAIN_ENDPOINT / name + '/',
        )

        if response.is_error:
            z_response.error = response.text

        z_response.data = response.json()

        return z_response

    def delete(self, name: str, version: int, collection: str = DEFAULT_COLLECTION):
        raise NotImplementedError()

    def run(self, name: str, version: int, collection: str = DEFAULT_COLLECTION) -> dict:
        raise NotImplementedError()
