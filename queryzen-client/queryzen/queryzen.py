"""
TODO: Add docstring explaining what's in the file.
"""

import dataclasses
import datetime
import json
import typing
from typing import Any, Generator

from . import constants
from .sql import safe_sql_replace, parse_parameters
from .backend import QueryZenHttpClient, QueryZenClientABC
from .exceptions import (UncaughtBackendError,
                         ZenDoesNotExistError,
                         ZenAlreadyExistsError,
                         ExecutionEngineError,
                         MissingParametersError,
                         DatabaseDoesNotExistError,
                         DefaultValueDoesNotExistError,
                         ParametersMissmatchError)
from .types import AUTO, Rows, Columns, _AUTO, Default, ZenState
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
        started_at: The time the query was executed in UTC.
        finished_at: The time the query finished running in UTC.
        total_time: Time in ms that took for the query to run.
        query: The query that produced this result.
    """
    id: str
    row_count: int
    state: str
    started_at: datetime.datetime
    finished_at: datetime.datetime
    total_time: int
    query: str
    error: str = ''
    parameters: dict = dataclasses.field(default_factory=dict)
    rows: Rows = dataclasses.field(repr=False, default_factory=list)
    columns: Columns = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.parameters, str):
            try:
                self.parameters = json.loads(self.parameters)
            except json.JSONDecodeError as e:
                raise ValueError('cannot json.loads parameters') from e

    @property
    def is_error(self):
        return bool(self.error)

    def has_data(self):
        return self.row_count > 0

    def as_table(self, column_center: ColumnCenter = 'left'):
        if not self.rows:
            if self.is_error:
                rows = [(self.error,), ]
            else:
                rows = (['' for _ in range(len(self.columns))],)
        else:
            rows = self.rows
        return make_table(columns=self.columns or ['no data'] if not self.is_error else ['error'],
                          rows=rows,
                          column_center=column_center)

    def as_polars(self) -> 'polars.DataFrame':
        try:
            import polars  # pylint: disable=C0415
        except ImportError as e:
            raise ImportError('polars is needed to use `as_polars`,'
                              ' try installing it with `pip install polars`') from e
        return polars.from_records(self.rows, orient='row', schema=self.columns)

    def to_dict(self) -> dict:
        """Transform the instance into a dictionary"""
        return dataclasses.asdict(self)

    def row_at(self, i: int) -> list:
        """Returns the row number i.

        Raises:
            Index error if row i does not exist.

        Returns:
            The at position i
        """

        return self.rows[i]

    def iter_rows(self):
        """Iterate over rows

        Returns:
            An iterator of rows.
        """
        return iter(self.rows)

    def iter_cols(self) -> Generator[list[Any], Any, None]:
        """Iterate over columns, it copies items so it is not the most memory efficient.

        Returns:
            A generator of columnar values.
        """
        for i in range(len(self.columns)):
            col = []
            for j in range(self.row_count):
                col.append(self.rows[j][i])
            yield col

    def __iter__(self):
        return self.iter_rows()


@dataclasses.dataclass
class ZenStatistic:
    """
    A data class representing statistical metrics for execution time analysis.
    If a Zen has no executions, all metrics will return None.
    Attributes:
        min_execution_time_ms (int | None): The minimum execution time in milliseconds.
        max_execution_time_ms (int | None): The maximum execution time in milliseconds.
        mean_execution_time_ms (float | None): The mean (average) execution time in milliseconds.
        mode_execution_time_ms (int | None): The most frequently occurring execution
         time in milliseconds.
        median_execution_time_ms (int | None): The median execution time in milliseconds.
        variance (float | None): The statistical variance of execution times.
        standard_deviation (float | None): The standard deviation of execution times.
        range (float | None): The difference between max and min execution times.
    """
    min_execution_time_ms: int | None
    max_execution_time_ms: int | None
    mean_execution_time_ms: float | None
    mode_execution_time_ms: int | None
    median_execution_time_ms: int | None
    variance: float | None
    standard_deviation: float | None
    range: float | None

    def to_dict(self) -> dict:
        """Transform the instance into a dictionary"""
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Zen:
    """A ``Zen`` is a named and versioned SQL query that lives in a QueryZen backend"""
    id: int
    name: str
    version: int
    query: str
    description: str
    created_at: datetime.datetime
    default_parameters: dict = dataclasses.field(default_factory=dict)
    collection: str = dataclasses.field(default_factory=lambda: DEFAULT_COLLECTION)
    created_by: str = dataclasses.field(default_factory=lambda: 'not_implemented')
    state: ZenState = dataclasses.field(default_factory=lambda: 'unknown')
    executions: list[ZenExecution] = dataclasses.field(default_factory=list)  # Improve typing

    def to_dict(self) -> dict:
        """Transform the instance into a dictionary"""
        return dataclasses.asdict(self)

    def difference(self, other: 'Zen', compare: list[str] = None) -> dict[str: tuple]:
        """Returns a dictionary with the difference between 'Zen's, it only
        compares name, version and query. You can specify which fields to compare with the
        ``compare`` parameter.

        >>> Zen.empty().difference(Zen.empty())
        {}

        >>> Zen(name='name1', ...).difference(Zen(name='name2', ...))
        {'name': ('name1', 'name2'), ...}

        """
        if not isinstance(other, Zen):
            raise TypeError('Can only check between Zen instances')

        if not compare:
            compare = ['name', 'description', 'version']

        difference = {}
        s = self.to_dict()
        o = other.to_dict()

        for key in compare:
            if not o[key] == s[key]:
                difference[key] = (s[key], o[key])
        return difference

    @classmethod
    def empty(cls):
        """Returns an empty Zen, used for testing and debugging or when you just need an empty Zen.

        Integer values are -1 and string values are '_', anything else might be a -1 even
        """
        return Zen(id=-1,
                   name='_',
                   version=-1,
                   query='_',
                   description='-1',
                   created_at=datetime.datetime(year=1978, month=12, day=6))

    def preview(self, **parameters) -> str:
        """Previews the SQL that would be run given the parameters in QueryZen, if a parameter
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
    """QueryZen client.

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

    def _validate_version(self, version) -> str:
        """
            Validate the input `version` value.

            This method ensures that the provided `version` is either an integer or a special
            sentinel value `_AUTO`. If it is an integer, it will be converted to a string.
            Otherwise, a `ValueError` is raised.

        Args:
            version: The version value to validate. Must be of type `int` or `_AUTO`.

        Returns:
            str: The version as a string, if it's a valid integer.

        Raises:
            ValueError: If `version` is not an integer or `_AUTO`.
        """
        if not isinstance(version, (int, _AUTO)):
            raise ValueError('zen version should be an integer')
        if isinstance(version, int):
            version = str(version)
        return version

    def create(self,
               name: str,
               query: str,
               description: str = None,
               collection: str = DEFAULT_COLLECTION,
               version: _AUTO | int = AUTO,
               default: Default | dict[str: typing.Any] = None) -> Zen:
        """Creates a Zen.

        Args:
            name: The name of the Zen
            query: The query of the Zen
            version: The version of the zen, if AUTO is set, it will take the latest one and add one
            collection: The collection of the Zen, defaults to ``DEFAULT_COLLECTION``
            description: The description of the Zen.
            default: Default values for the query parameters.

        Raises:
            ZenAlreadyExists: If you try to create a Zen that already exists, use default version
            to avoid this.

            UncaughtBackendError: If the backend returns an uncaught error, the user
            is never meant to get this.

        Returns:
            The created Zen.
        """

        if default:
            parameters = parse_parameters(query)

            if isinstance(default, dict):
                default = Default(**default)
            elif not isinstance(default, Default):
                raise ValueError(f'default has to be {dict!r}'
                                 f' or {Default!r}, not {type(default)!r}')

            has_all, missing = default.missing_parameters(parameters)

            if not has_all:
                raise DefaultValueDoesNotExistError(f'default received a parameter'
                                                    f' that is not in the query: {missing!r}')

        response = self._client.create(collection=collection,
                                       name=name,
                                       version=version,
                                       query=query,
                                       description=description,
                                       default=default)

        if response.error:
            if response.error_code == 409:
                raise ZenAlreadyExistsError()

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
            ... try:
            ...     zen = qz.get(name='myzen', version=23)
            ... except ZenDoesNotExistError:
            ...     handle_zen_not_existing()

        Raises:
            ZenDoesNotExistError: if the ``Zen`` does not exist.

            If you don't want to manually handle if the query exists,
            check ``QueryZen.get_or_create``

        Returns:
            ``Zen`` if it exists.
        """
        version = self._validate_version(version)

        response = self._client.get(name=name,
                                    version=version,
                                    collection=collection)

        if response.error:
            if response.error_code == 404:
                raise ZenDoesNotExistError()

            raise UncaughtBackendError(response=response,
                                       zen=Zen.empty(),
                                       context='Getting a Zen')
        executions = [ZenExecution(**kw) for kw in response.data[0].pop('executions')]

        zen = Zen(**response.data[0])
        zen.executions = executions
        return zen

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
            ...    do_something_with_zens(zens)

            # Will return all ``Zen``s with name 'mountain'
            # who has at least one execution that was invalid.

        Returns:
             A list of ``Zen``, empty list if none is found.
        """
        response = self._client.filter(**filters)

        if response.error:
            raise UncaughtBackendError(response,
                                       zen=Zen.empty(),
                                       context='Listing Zens')

        return [Zen(**data) for data in response.data]

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
            ...    zen = qz.get('z', version=3)
            ...    qz.delete(zen)
            ...except ZenDoesNotExistError:
            ...    pass

        Returns:
            Nothing.

        Raises:
            ZenDoesNotExistError: If the zen being deleted does not exist.
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
            factory: typing.Any = None,
            **params):
        """Runs a zen with the given parameters.

        Args:
            zen: The zen to run.
            database: The database the Zen will be run to, if none is defined, the default
                one will be used. If you only have one defined, that will be the default.
            timeout: Time in seconds the backend will take until returning a timeout error
                default time is 30 seconds, if you expect your queries to take more,
                 increase the value.
            factory: Factory to be used to create rows, typically a dataclass or a pydantic model
            params: Parameters to send to the backend for the query.

        Backend Parameters:
            Todo: Add. (There are currently none)

        Examples:
            # Create and run a simple Zen.
            >>>from queryzen import QueryZen
            >>>qz = QueryZen()
            >>>zen = qz.create('q', 'select 1')
            >>>result = qz.run(zen, database='postgres_main', timeout=1000)
            >>>result.as_table()

            TODO: Add more examples:
            # Create and run a parametrized Zen.
            # Run a zen with factory
        """
        response = self._client.run(name=zen.name,
                                    collection=zen.collection,
                                    version=zen.version,
                                    database=database,
                                    timeout=timeout,
                                    parameters=params)

        if response.error:
            if response.error_code == 400:
                raise MissingParametersError(response.error)

            if response.error_code == 409:
                raise ParametersMissmatchError(response.error)

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

        rows = response.get_from_data('rows')

        if factory and rows:
            rows = list(map(lambda row: factory(*row), rows))

        execution = ZenExecution(id=response.get_from_data('id'),
                                 rows=rows,
                                 columns=response.get_from_data('columns'),
                                 row_count=len(response.get_from_data('rows'))
                                 if not hasattr(response.data[0], 'row_count')
                                 else response.get_from_data('row_count'),
                                 state=response.get_from_data('state'),
                                 started_at=response.get_from_data('started_at'),
                                 finished_at=response.get_from_data('finished_at'),
                                 total_time=response.get_from_data('total_time'),
                                 parameters=response.get_from_data('parameters'),
                                 error=response.get_from_data('error'),  # execution error
                                 query=response.get_from_data('query'))
        zen.executions.append(execution)

        # Update state.
        zen.state = execution.state

        return execution

    def stats(self,
              name: str,
              collection=DEFAULT_COLLECTION,
              version: _AUTO | int = AUTO,
              ) -> ZenStatistic:
        """
        Return zen statistics.

        Args:
            name: The name of the ``Zen``
            collection: The collection of the `Zen`, defaults to ``DEFAULT_COLLECTION``.
            version: The version of the `Zen`, defaults to 'AUTO'.

        Raises:
            ZenDoesNotExistError: if the ``Zen`` does not exist.

            If you don't want to manually handle if the query exists,
            check ``QueryZen.get_or_create``

        Returns:
            ``ZenStatistic`` if it exists or ``None``.
        """

        version = self._validate_version(version)
        response = self._client.stats(collection, name, version)

        if response.error:
            if response.error_code == 404:
                raise ZenDoesNotExistError(
                    'You are trying to get stats from a zen that does not exist'
                )

        return ZenStatistic(**response.data[0])  # Statistics always return one element
