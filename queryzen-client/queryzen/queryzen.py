"""
TODO: Add docstring explaining what's in the file.
"""

import dataclasses
import datetime
import typing

from . import constants
from .sql import safe_sql_replace
from .backend import QueryZenHttpClient, QueryZenClientABC
from .exceptions import (
    UncaughtBackendError,
    ZenDoesNotExistError,
    ZenAlreadyExists,
    ExecutionEngineError,
    MissingParametersError, DatabaseDoesNotExistError
)
from .types import AUTO, Rows, Columns, _AUTO
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
        execution_duration_ms: The milliseconds it took the query to run.
        query: The query that produced this result.
    """
    rows: Rows = dataclasses.field(repr=False)
    columns: Columns
    row_count: int
    executed_at: datetime.datetime
    finished_at: datetime.datetime
    execution_duration_ms: int
    query: str
    error: str = ''

    @property
    def is_error(self):
        return bool(self.error)

    def has_data(self):
        return self.row_count > 0

    def as_table(self, column_center: ColumnCenter = 'left'):
        return make_table(columns=self.columns if self.columns else ['error'],
                          rows=self.rows if self.rows else [(self.error,), ],
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

    def preview(self, **parameters) -> str:
        """
        Previews the SQL that will be computed given the parameters in QueryZen, if a parameter
        is missing, it will not raise an exception, this is mainly for debugging purposes,
        read ``run`` to see how missing parameters are handled.

        Args:
            parameters: The parameters that will be injected into the query.

        Examples:
            >>> zen = Zen(name='myzen', query='SELECT * FROM t WHERE val > :val')
            >>> zen.preview(val=1)
            'SELECT * FROM t WHERE val > 1'

        Returns:
            The query with the parameters.
        """
        return safe_sql_replace(self.query, parameters)


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
               collection: str = DEFAULT_COLLECTION,
               version: _AUTO | int = AUTO) -> Zen:
        """Creates a Zen.

        Args:
            name: The name of the Zen
            query: The query of the Zen
            version: The version of the zen, if AUTO is set, it will take the latest one and add one
            collection: The collection of the Zen, defaults to ``DEFAULT_COLLECTION``
            description: The description of the Zen.
        """
        response = self._client.create(collection=collection,
                                       name=name,
                                       version=version,
                                       query=query,
                                       description=description)

        if response.error:
            if response.error_code == 409:
                raise ZenAlreadyExists()

            raise UncaughtBackendError(response=response,
                                       zen=Zen(id=-1,
                                               version=-1,
                                               created_at=None,
                                               name=name,
                                               query=query,
                                               collection=collection,
                                               description=description),
                                       context='This was raised while creating a Zen.')

        if not response.data:
            raise UncaughtBackendError(response=response,
                                       zen=Zen(id=-1,
                                               version=-1,
                                               created_at=-1,
                                               name=name,
                                               query=query,
                                               collection=collection,
                                               description=description),
                                       context='When creating a Zen, the JSON representation '
                                               'of the object was not returned')

        return Zen(**response.data[0])

    def get(self,
            name: str,
            collection=DEFAULT_COLLECTION,
            version: _AUTO | int = AUTO) -> Zen:
        """Get one zen from the given name, collection and version.

        Args:
            name: The name of the ``Zen``
            collection: The collection of the `Zen`, defaults to ``DEFAULT_COLLECTION``.
            version: The version of the `Zen`, defaults to 'AUTO'.

        If the version is set to AUTO, it will always fetch the latest one, being the latest
        one the one with the highest version number.

        Example:
            >>> qz = QueryZen()
            >>> try:
            >>>     zen = qz.get(name='myzen', version=23)
            >>> except ZenDoesNotExist:
            >>>     handle_zen_not_existing()

        Raises:
            ``ZenDoesNotExistError``: if the ``Zen`` does not exist.

            If you don't want to manually handle if the query exists,
            check ``QueryZen.get_or_create``

        Returns:
            ``Zen`` if it exists.
        """
        if not isinstance(version, (int, _AUTO)):
            raise ValueError('zen version should be an integer')

        if isinstance(version, int):
            version = str(version)

        response = self._client.get(name=name,
                                    version=version,
                                    collection=collection)

        if response.error:
            if response.error_code == 404:
                raise ZenDoesNotExistError()

            raise UncaughtBackendError(response=response,
                                       zen=Zen.empty(),
                                       context='Getting a Zen')

        return Zen(**response.data[0])

    def filter(self, **filters) -> list[Zen]:
        """Filters all ``Zen``.

        Accepts advanced filters like: [`name`, `collection`, `version`, `state`, `executions`...]

        This method uses a special filtering endpoint that is different from the REST endpoints.

        If you now exactly the collection, name and version use ``QueryZen.get`` or
         ``QueryZen.get_or_create``, only use this one for advanced filtering and statistics.

        Args:
            filters: The filters that will be used.

        Example:
            >>>qz = QueryZen()
            >>>zens = qz.filter(name='mountain', collection_contains='prod', executions__state='IN')
            >>>if zens:
            >>>    do_something_with_zens(zens)
            # Will return all ``Zen``s with name 'mountain' who has at least one execution that was
            invalid.
            ```
        Returns:
             A list of ``Zen``, empty list if none is found.
        """
        response = self._client.filter(**filters)

        if response.error:
            raise UncaughtBackendError(response,
                                       zen=Zen.empty(),
                                       context='Listing Zens')

        return [
            Zen(**data) for data in response.data
        ]

    def get_or_create(self,
                      name: str,
                      query: str,
                      collection: str = DEFAULT_COLLECTION) -> (bool, Zen):
        """Get a ``Zen`` or create it.

        Args:
            name: The name of the Zen.
            query: The query (only used if created).
            collection: The collection of the Zen (defaults to ``DEFAULT_COLLECTION``).

       Examples:
            >>> qz = QueryZen()
            >>> created, zen = qz.get_or_create('zen', query='select * from t where h > :value')
            False, Zen(name='myzen', version='latest', ...)

            >>> _, zen = QueryZen().get_or_create(name='z', query='q', version=34)
            True, Zen(name='z', ...)

        Returns:
            A tupe (created, Zen), the first element is a bool on whether the zen was
            created or not, the second element is the Zen.
        """
        try:
            return False, self.get(name=name, collection=collection)
        except ZenDoesNotExistError:
            return True, self.create(name=name, collection=collection, query=query)

    def delete(self, zen: Zen) -> None:
        """Deletes a Zen

        Args:
            zen: The zen to delete.

        Examples:
            # Delete the latest Zen with name 'myzen'.
            >>>from queryzen import QueryZen
            >>>qz = QueryZen()
            >>>zen = qz.get(name='myzen')
            >>>qz.delete(zen)

            # Delete a Zen by version.
            >>>try:
            >>>    zen = qz.get('z', version=3)
            >>>    qz.delete(zen)
            >>>except ZenDoesNotExistError:
            >>>    pass

        Returns:
            Nothing.

        Raises:
            ``ZenDoesNotExistError`` If the zen being deleted does not exist.
        """
        response = self._client.delete(zen)

        if response.error:
            if response.error_code == 404:
                raise ZenDoesNotExistError('You are trying to delete a Zen that does not exist')
            raise UncaughtBackendError(response,
                                       zen=zen,
                                       context='Deleting Zen')

    def run(self,
            zen: Zen,
            database: str = constants.DEFAULT_DATABASE,
            timeout: int = int(constants.DEFAULT_ZEN_EXECUTION_TIMEOUT),
            **params):
        """Runs a zen with the given parameters.

        Args:
            zen: The zen to run.
            database: The database the Zen will be run to, if none is defined, the default
                one will be used. If you only have one defined, that will be the default.
            timeout: Time in seconds the backend will take until returning a timeout error
                default time is 30 seconds, if you expect your queries to take more,
                 increase the value.
            params: Parameters to send to the backend.

        Backend Parameters:
            Todo: Add. (There are currently none)

        Examples:
            # Create and run a simple Zen.
            >>>from queryzen import QueryZen
            >>>qz = QueryZen()
            >>>zen = qz.create('q', 'select 1')
            >>>result = qz.run(zen, database='postgres_main', timeout=1000)
            >>>result.as_table()

            # Create and run a parametrized Zen.
        """
        response = self._client.run(name=zen.name,
                                    collection=zen.collection,
                                    version=zen.version,
                                    database=database,
                                    timeout=timeout,
                                    **params)

        if response.error:
            if response.error_code == 400:
                raise MissingParametersError(response.error)

            if response.error_code == 503 or response.error_code == 408:
                raise ExecutionEngineError(response.error)

            if response.error_code == 404:
                raise ZenDoesNotExistError('You are trying to run a Zen that does not exist')

            if response.error_code == 416:
                raise DatabaseDoesNotExistError(response.error)
            raise UncaughtBackendError(response,
                                       zen=zen,
                                       context=f'Running a Zen with: params {params}')

        if not response.data:
            raise UncaughtBackendError(response,
                                       zen=zen,
                                       context='Backend returned ok but did not send data back')
        execution = ZenExecution(rows=response.get_from_data('rows'),
                                 columns=response.get_from_data('columns'),
                                 row_count=len(response.get_from_data('rows'))
                                 if not hasattr(response.data[0], 'row_count')
                                 else response.get_from_data('row_count'),
                                 executed_at=response.get_from_data('executed_at'),
                                 finished_at=response.get_from_data('finished_at'),
                                 execution_duration_ms=response.get_from_data('execution_time_ms'),
                                 error=response.get_from_data('error'), # execution error
                                 query=response.get_from_data('query'))
        zen.executions.append(execution)
        return execution
