"""
TODO: Add docstring explaining what's in the file.
"""

import dataclasses
import datetime
import typing

from .backend import QueryZenHttpClient, QueryZenClientABC
from .exceptions import ZenDoesNotExist, UncaughtBackendError
from .types import AUTO, Rows, Columns
from .constants import DEFAULT_COLLECTION


@dataclasses.dataclass
class ZenExecution:
    """
    Represents the execution of a Zen in a Zen backend.
    """
    rows: Rows
    columns: Columns
    row_count: int

    def has_data(self):
        return self.row_count > 0



@dataclasses.dataclass
class Zen:
    """
    A ``Zen`` is a named and versioned SQL query that lives in a QueryZen backend.
    """
    id: int
    name: str
    version: int
    query: str
    description: str
    created_at: datetime.datetime
    collection: str = dataclasses.field(default_factory=lambda: DEFAULT_COLLECTION)
    created_by: str = dataclasses.field(default_factory=lambda: 'not_implemented')
    state: typing.Literal['valid', 'invalid', 'unknown'] = dataclasses.field(
        default_factory=lambda: 'unknown')
    executions: list = dataclasses.field(default_factory=list)  # Improve typing

    def to_dict(self) -> dict:
        """Transform the instance into a dictionary"""
        return dataclasses.asdict(self)

    def difference(self, other: 'Zen') -> dict:
        """
        Returns a dictionary with the difference between to 'Zen', it only
        compares name, version and query.
        """
        keys = ['name', 'description', 'version']


        difference = {}
        s = self.to_dict()
        o = other.to_dict()

        if not isinstance(other, Zen):
            raise TypeError('Can only check between Zen instances')

        for key in keys:
            if not o[key] == s[key]:
                difference[key] = (s[key], o[key])
        return difference

    @classmethod
    def empty(cls):
        """Returns an empty Zen, used for testing and debugging."""
        return Zen(id=-1, name='_', version=-1, query='_', description='-1', created_at=-1)

class QueryZen:
    """
    QueryZen client.

    # Todo add examples from README.md
    Examples:

        ```
        from queryzen import QueryZen

        qz = QueryZen()

        qz.create(...)

        ```
    """
    def __init__(self, client: QueryZenClientABC | None = None):
        self._client: QueryZenClientABC = client or QueryZenHttpClient()

    def create(
            self,
            name: str,
            query: str,
            description: str = None,
            collection: str = DEFAULT_COLLECTION
    ):
        response = self._client.create(
            name=name,
            query=query,
            collection=collection,
            description=description
        )

        if response.error:
            raise UncaughtBackendError(
                response=response,
                zen=Zen(
                    id=-1,
                    version=-1,
                    created_at=None,
                    name=name,
                    query=query,
                    collection=collection,
                    description=description
                ),
                context='This was raise while creating a Zen.'
            )

        if not response.data:
            raise UncaughtBackendError(
                response=response,
                zen=Zen(
                    id=-1,
                    version=-1,
                    created_at=-1,
                    name=name,
                    query=query,
                    collection=collection,
                    description=description
                ),
                context='When creating a Zen, the JSON representation '
                        'of the object was not returned'
            )

        return Zen(**response.data[0])

    def get(self, name: str, collection=DEFAULT_COLLECTION, version=AUTO) -> Zen:
        """
        Get one zen from the given name, collection and version, raises ``ZenDoesNotExist``
        if it does not exist.

        If you don't want to handle if the query does not exist and just want a `Zen`,
        see ``QueryZen.get_or_create``.

        Args:
            name: The name of the ``Zen``
            collection: The collection of the `Zen`, defaults to ``DEFAULT_COLLECTION``.
            version: The version of the `Zen`, defaults to 'AUTO'.

        Example:
            qz = QueryZen()

            try:
                zen = qz.get(name='myzen', version=23)

            except ZenDoesNotExist:
                handle_zen_not_existing()

        Raises:
            `ZenDoesNotExist` if the `Zen` does not exist.

        Returns:
            A zen, if it exists.
        """
        response = self._client.get(
            name=name,
            version=version,
            collection=collection
        )

        if not response.data:
            raise ZenDoesNotExist()

        if response.error:
            raise UncaughtBackendError(
                response=response,
                zen=Zen.empty(),
                context='Getting a Zen'
            )

        return Zen(**response.data[0])

    def list(self, **filters) -> list[Zen]:
        """
        Lists all ``Zen``, accepts additional filters like `name`, `collection`, `version`
        # todo add execution filter

        This method uses a special filtering endpoint that is different from the REST endpoints we
        use, it offers special filtering options like filtering by execution sub parameters,
        see examples for use cases.

        It does not raise Exceptions, if you want to be extra safe,
        use QueryZen.get or QueryZen.get_or_create

        Args:
            filters: The filters that will be used.

        Examples:

            ```
            qz = QueryZen()

            zens = qz.list(name='mountain', executions__status='VALID')
            if zens:
                do_something_with_zens(zens)
            # Will return all ``Zen``s with name 'mountain' whose execution status is valid
            # todo check wording on this
            ```

        Returns:
             A list of ``Zen``, empty if none is found.
        """
        response = self._client.list(**filters)

        if response.error:
            raise UncaughtBackendError(
                response,
                zen=Zen.empty(),
                context='Listing Zens'
            )

        return [
            Zen(**data) for data in response.data
        ]

    def get_or_create(
            self,
            name: str,
            query: str,
            collection: str = DEFAULT_COLLECTION
    ) -> (bool, Zen):
        """
        Get a Zen or create it.


        Examples:
            >>> qz = QueryZen()
            >>> created, zen = qz.get_or_create('zen', query='select * from t where h > :value')
            False, Zen(name='myzen', version='latest', ...)

            >>> _, zen = QueryZen().get_or_create(name='z', query='q', version=34)
            True, Zen(name='z', ...)

        Args:
            name: The name of the Zen.
            query: The query (only used if created).
            collection: The collection of the Zen (defaults to ``DEFAULT_COLLECTION``).
            version: The version of the Zen (defaults to ``AUTO``, the latest will be returned).

        Returns:
            (created, Zen) Returns a tuple, the first element is a bool on whether the zen was
            created or not, the second element is the Zen.
        """
        try:
            return False, self.get(name=name, collection=collection)
        except ZenDoesNotExist:
            return True, self.create(name=name, collection=collection, query=query)

    def delete(self):
        raise NotImplementedError

    def run(self, **params) -> None:
        raise NotImplementedError
