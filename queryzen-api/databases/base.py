"""ABC for QueryZen Database drivers."""

import abc
import dataclasses
import logging
import re

import sqlite3

import httpx

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    # Todo move exception to right place and rename it.
    pass


@dataclasses.dataclass
class DatabaseResponse:
    """Represents a Response from a Database call"""
    rows: list
    columns: list
    query: str
    query: str
    row_count: int = 0


class Database(abc.ABC):
    """Base class for all Databases """
    connection = None

    def prepare_query(self, query: str, parameters):
        """Prepares the query with parameters."""
        return safe_sql_replace(query, parameters)

    def execute_query(self, query: str, parameters: dict) -> DatabaseResponse:
        """Prepares the context and calls run_query, if you are implementing a Driver, do not
        touch this one
        """
        query = self.prepare_query(query, parameters)
        context = dict(raw_query=query, parameters=dict)
        return self.run_query(context, query)

    @abc.abstractmethod
    def run_query(self, context, query) -> DatabaseResponse:
        """The method for Database drivers to implement."""
        pass


class SQLiteDatabase(Database):
    """Sqlite 3"""

    def __init__(self, database, *args, **kwargs):
        self.connection = sqlite3.connect(database, *args, **kwargs)

    def run_query(self, context, query) -> DatabaseResponse:
        """
        Executes a SQL statement and returns the resulting cursor.
        """
        columns = []
        cursor = self.connection.cursor()
        result = cursor.execute(query)
        rows = result.fetchall()
        if cursor.description:
            columns = [x for xs in cursor.description for x in xs if x is not None]
        cursor.close()

        return DatabaseResponse(columns=columns,
                                rows=rows,
                                query=query,
                                row_count=len(rows))


def safe_sql_replace(sql: str,
                     parameters: dict,
                     char_delimiter: str = ':',
                     quote_ident_with: str = '"') -> str:
    """Replaces parameters in an SQL statement with values from a dictionary.

    Supports integers, strings, and null values while ensuring proper escaping.
    Supports special function 'IDENT', to quote identities.

    Args:
        sql: The SQL statement with :parameter placeholders.
        parameters: Dictionary containing parameter names and values.
        char_delimiter: Character prefix for placeholders (default: ':').
        quote_ident_with: Character for quoting IDENT values (default: '"').

    Raises:
        ValueError: If an unsupported data type is encountered.

    Returns:
        The SQL statement with placeholders replaced by values.

    Examples:
        >>> safe_sql_replace('select IDENT(:col) FROM tbl1 t WHERE t.value =
        ... :var1 and t.name = :var2', {'col': 'col1', 'var1': 1, 'var2': 'somename'})
        select "col1" FROM tbl1 t WHERE t.value = 1 and t.name = 'somecol'
    """

    def format_value(value):
        """Formats the value inside the string depending on type."""
        if isinstance(value, str):
            # Escape single quotes.
            value = value.replace("'", "''")

            # Wrap the value in single quotes
            replacement = f"'{value}'"
            return replacement

        if isinstance(value, (int, float)):
            return str(value)

        if value is None:
            return 'NULL'

        raise ValueError(f'unsupported parameter type: {type(value)}')

    for key, value in parameters.items():
        replacement = format_value(value)
        to_replace = char_delimiter + key

        # Replace FIELD(:value) with quoted value
        sql = re.sub(rf'IDENT\({to_replace}\)',
                     replacement.replace("'", quote_ident_with),
                     sql)

        # Replace :value with actual value
        sql = re.sub(rf'(?<!\w){to_replace}(?!\w)',
                     replacement,
                     sql)

    return sql


class CrateDatabase(Database):
    """CrateDB"""

    def run_query(self, context, query):
        response = httpx.post('http://crate:4200/_sql',
                              json={'stmt': query})

        data = response.json()
        if response.is_success:
            return DatabaseResponse(columns=data.get('cols'),
                                    rows=data.get('rows'),
                                    query=query,
                                    row_count=data.get('rowcount'))
        else:
            raise DatabaseError(response.json().get('error').get('message'))
