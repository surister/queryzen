import dataclasses
import datetime
import typing

from queryzen.backend import QueryZenHttpClient, QueryZenClientABC
from queryzen.exceptions import ZenAlreadyExists, UnknownError, ZenDoesNotExist
from queryzen.types import AUTO


class ZenExecution:
    """
    Represents the execution of a Zen in a Zen backend.
    """


@dataclasses.dataclass
class Zen:
    id: int
    name: str
    version: str
    query: str
    description: str
    created_at: datetime.datetime
    collection: str = dataclasses.field(default_factory=lambda: "main")
    created_by: str = dataclasses.field(default_factory=lambda: "not_implemented")
    state: typing.Literal['valid', 'invalid', 'unknown'] = dataclasses.field(
        default_factory=lambda: 'unknown')
    executions: list = dataclasses.field(default_factory=list)  # Improve typing

    def to_dict(self):
        return dataclasses.asdict(self)


class QueryZen:
    def __init__(
            self,
            client: QueryZenClientABC | None = None
    ):
        self._client = client or QueryZenHttpClient()

    def create(
            self,
            name: str,
            query: str,
            description: str = None,
            collection: str = 'main',
            version=AUTO
    ):
        response = self._client.create(
            name=name,
            query=query,
            collection=collection,
            description=description,
            version=version
        )

        if response.error:
            if response.error_code == 409:
                raise ZenAlreadyExists(response.error)
            raise UnknownError(response.error)

        return Zen(**response.data[0])

    def get(self, name: str, version=AUTO) -> Zen | None:
        response = self._client.get_one(
            name=name,
            version=version
        )

        if not response.data:
            raise ZenDoesNotExist()

        if not response.error:
            return Zen(**response.data[0])

    def list(self, **filters) -> list[Zen]:
        """
        Lists all ``Zen``, accepts additional filters like 'name', 'collection', 'version' # todo add execution filter
        :return:
        """
        response = self._client.get_all(**filters)
        if not response.error:
            return [
                Zen(**data) for data in response.data
            ]

    def run(self, **params) -> None:
        raise NotImplementedError

