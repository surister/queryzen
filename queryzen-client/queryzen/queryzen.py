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
from .table import make_table, ColumnCenter


@dataclasses.dataclass
class ZenExecution:
    """
    Represents the execution of a Zen in a Zen backend. If backend does not return row_count,
    we compute it ourselves with `len(rows)`, if there are a lot it could be slow, ideally the
    database also returns the row_count.

    Args:
        rows: The rows of the response.
        columns: The columns of the response.
        row_count: How many rows there are.
        executed_at: The time the query was executed in UTC.
        finished_at: The time the query finished running in UTC.
        execution_duration: The milliseconds it took the query to run.
    """
    rows: Rows
    columns: Columns
    row_count: int
    executed_at: datetime.datetime
    finished_at: datetime.datetime
    execution_duration: int

    def has_data(self):
        return self.row_count > 0

    def as_table(self, column_center: ColumnCenter = 'left'):
        return make_table(columns=self.columns,
                          rows=self.rows,
                          column_center=column_center)

    def iter_rows(self):
        return iter(self.rows)

    def iter_cols(self):
        pass


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
    executions: list[ZenExecution] = dataclasses.field(default_factory=list)  # Improve typing

    def to_dict(self) -> dict:
        """Transform the instance into a dictionary"""
        return dataclasses.asdict(self)

    def difference(self, other: 'Zen', compare: list[str] = None) -> dict[str: tuple]:
        """
        Returns a dictionary with the difference between 'Zen's, it only
        compares name, version and query. You can specify which fields to compare in the
        ``compare`` parameter.

        >>> Zen.empty().difference(Zen.empty())
        {}

        >>> Zen(name='name1', ...).difference(Zen(name='name2', ...))
        {'name': ('name1', 'name2'), ...}

        """
        if not compare:
            compare = ['name', 'description', 'version']

        difference = {}
        s = self.to_dict()
        o = other.to_dict()

        if not isinstance(other, Zen):
            raise TypeError('Can only check between Zen instances')

        for key in compare:
            if not o[key] == s[key]:
                difference[key] = (s[key], o[key])
        return difference

    @classmethod
    def empty(cls):
        """
        Returns an empty Zen, used for testing and debugging or when you just need an empty Zen.

        Integer values are -1 and string values are '_', anything else might be a -1 even
        """
        return Zen(id=-1,
                   name='_',
                   version=-1,
                   query='_',
                   description='-1',
                   created_at=datetime.datetime(year=1978, month=12, day=6))

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

    def create(self,
               name: str,
               query: str,
               description: str = None,
               collection: str = DEFAULT_COLLECTION):
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

    def get(self,
            name: str, collection=DEFAULT_COLLECTION,
            version=AUTO) -> Zen:
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

        Returns:
            (created, Zen) Returns a tuple, the first element is a bool on whether the zen was
            created or not, the second element is the Zen.
        """
        try:
            return False, self.get(name=name, collection=collection)
        except ZenDoesNotExist:
            return True, self.create(name=name, collection=collection, query=query)

    def delete(self, zen: Zen) -> bool:
        """
        Deletes a Zen

        Args:
            zen: The zen to delete.

        Examples:

            Delete the latest Zen.

            ```

            from queryzen import QueryZen

            qz = QueryZen()

            zen = qz.create('z', 'select 1')

            qz.delete(zen)

            ```

            Delete a Zen by version.

            ```

            from queryzen import QueryZen

            qz = QueryZen()

            try:
                zen = qz.get('z', version=3)
                qz.delete(zen)
            except queryzen.ZenDoesNotExist:
                print('Why are we trying to delete a Zen that does not exist?')

            ```

        Returns:
            if the zen was deleted.
        """
        response = self._client.delete(zen)

        if response.error:
            raise UncaughtBackendError(
                response,
                zen=zen,
                context='Deleting Zen'
            )
        return True

    def run(self, zen: Zen, **params):
        """
        Runs a zen with the given parameters.

        Args:
            zen: The zen to run.
            params: Parameters to send to the backend.


        Backend Parameters:
            ``timeout`` (int): Time in seconds the backend will take until returning a timeout error
            ``database`` (str): The database the Zen will be run to, if none is defined the default
            one will be used. If you only have one defined, that will be the default.

        Examples:
            ```

            from queryzen import QueryZen

            qz = QueryZen()

            q = qz.create('q', 'select 1')

            result = qz.run(q, timeout=1000, database='postgres_main')

            print(result.as_table())

            ```
        """
        response = self._client.run(
            name=zen.name,
            collection=zen.collection,
            version=zen.version,
            **params
        )

        if response.error:
            raise UncaughtBackendError(
                response,
                zen=zen,
                context=f'Running a Zen with: params {params}'
            )

        if not response.data:
            raise UncaughtBackendError(
                response,
                zen=zen,
                context='Backend returned ok but did not send data back'
            )
        execution = ZenExecution(
            rows=response.get_from_data('rows'),
            columns=response.get_from_data('columns'),
            row_count=len(response.get_from_data('rows'))
            if not hasattr(response.data[0], 'row_count') else response.get_from_data('row_count'),
            executed_at=response.get_from_data('executed_at'),
            finished_at=response.get_from_data('finished_at'),
            execution_duration=response.get_from_data('execution_time_ms')
        )
        zen.executions.append(execution)
        return execution
