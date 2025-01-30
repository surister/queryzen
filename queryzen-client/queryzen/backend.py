import abc
import dataclasses
import datetime
import os
import urllib

import httpx

from queryzen.types import _AUTO


class Url(str):
    """
    Represents an URL.
    """

    def __truediv__(self, other):
        return Url(
            self +
            f'{"/" if not self.endswith('/') else ""}' +
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
    def create(self, name, version, collection, description, query) -> QueryZenResponse:
        pass

    @abc.abstractmethod
    def get_one(self, name: str, version: str) -> QueryZenResponse:
        pass

    @abc.abstractmethod
    def get_all(self, **filters) -> list[QueryZenResponse]:
        pass

    @abc.abstractmethod
    def delete(self) -> QueryZenResponse:
        pass

    @abc.abstractmethod
    def run(self) -> QueryZenResponse:
        pass


class QueryZenHttpClient(QueryZenClientABC):
    """
    QueryZen HTTP implementation, the default implementation and implemented by QueryZen.

    This class handles the management of zens in sync with the HTTP backend developed by us.

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
               collection: str = 'main',
               description: str = '',
               query: str,
               ) -> QueryZenResponse:
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

    def get_all(self, **filters) -> QueryZenResponse:
        z_response = QueryZenResponse()

        response = httpx.get(
            self.url / self.MAIN_ENDPOINT / '?' + urllib.parse.urlencode(filters)
        )

        if response.is_error:
            z_response.error = response.text
        z_response.data = response.json()

        return z_response

    def get_one(self, name: str, version: int, collection: str = 'main') -> QueryZenResponse:
        """
        List all zens from a given name, version and collection can return many.
        """
        z_response = QueryZenResponse()

        response = self.client.get(
            self.url / self.COLLECTIONS / collection / self.MAIN_ENDPOINT / name + '/',
        )

        if response.is_error:
            z_response.error = response.text
        z_response.data = response.json()

        return z_response

    def delete(self, name, version):
        raise NotImplemented

    def run(self, name: str, version: int, parameters: dict) -> dict:
        raise NotImplemented
