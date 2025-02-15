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

    def _execute_query(self, query: str, parameters: dict) -> DatabaseResponse:
        """Prepares the context and calls run_query"""
        query = self.prepare_query(query, parameters)
        context = dict(raw_query=query, parameters=dict)
        return self.run_query(context, query)

    @abc.abstractmethod
    def run_query(self, context, query) -> DatabaseResponse:
        """The method for Database drivers to implement."""
        pass

"""Overrides this method to implement your own database operations."""


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


def safe_sql_replace(sql: str, parameters: dict, char_delimiter: str = ':') -> str:
    """Replaces :parameter placeholders in an SQL statement with values from a dictionary.

    It is resilient against injections; currently only both integers,
    string and null values can be used.

    Args:
        sql: The SQL statement with :parameter placeholders.
        parameters: A dictionary containing the parameter names and values.
        char_delimiter: The character to identify what to replace, defaults to ':', e.g. ':value'

    Raises:
        ``ValueError``: if the values are not integer, string or null.

    Returns:
        The SQL statement with placeholders replaced by values.

    Examples:
        >>> safe_sql_replace('select :val, :val1, :val2', {'val': 't', 'val1': 2, 'val2': "to"})
        select 't', 2, 'to'
    """
    for key, value in parameters.items():

        # Ensure the value is properly escaped
        if isinstance(value, str):
            # Escape single quotes.
            value = value.replace("'", "''")

            # Wrap the value in single quotes
            replacement = f"'{value}'"

        elif isinstance(value, (int, float)):
            # Use the value directly for numbers
            replacement = str(value)

        elif value is None:
            # Replace with NULL for None values
            replacement = 'NULL'

        else:
            raise ValueError(f'unsupported parameter type: {type(value)}')

        to_replace = char_delimiter + key
        sql = re.sub(rf'(?<!\w){to_replace}(?!\w)', replacement, sql)
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
            raise DatabaseError(response.text)
