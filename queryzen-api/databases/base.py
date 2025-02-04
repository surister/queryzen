import abc
import functools
import logging
import sqlite3

logger = logging.getLogger(__name__)


class Database(abc.ABC):
    connection = None

    @abc.abstractmethod
    def execute(self, sql, parameters=None):
        """Overrides this method to implement your own database operations."""
        pass


class SQLiteDatabase(Database):
    def __init__(self, database, *args, **kwargs):
        self.connection = sqlite3.connect(database, *args, **kwargs)

    def execute(self, sql, parameters=None) -> tuple:
        """
        Executes a SQL statement and returns the resulting cursor.
        """
        cursor = self.connection.cursor()
        result = cursor.execute(sql, parameters)
        rows = result.fetchall()
        columns = [x for xs in cursor.description for x in xs if x is not None]
        cursor.close()

        return columns, rows, 'unknown'


def safe_sql_replace(sql: str, parameters: dict) -> str:
    """
    Replaces :parameter placeholders in an SQL statement with values from a dictionary.

    Args:
        sql: The SQL statement with :parameter placeholders.
        parameters: A dictionary containing the parameter names and values.

    Raises:
        `ValueError` if the values are not integer, string or null

    Returns:
        The SQL statement with placeholders replaced by values.
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
            replacement = "NULL"

        else:
            raise ValueError(f"Unsupported parameter type: {type(value)}")

        placeholder = f":{key}"
        sql = sql.replace(placeholder, replacement)

    return sql


class CrateDatabase(Database):
    def execute(self, sql, parameters=None):
        sql = safe_sql_replace(sql, parameters)
        response = httpx.post('http://192.168.88.251:4200/_sql',
                              json={'stmt': sql})
        data = response.json()
        if response.is_success:
            return data.get('cols'), data.get('rows'), sql
        else:
            raise Exception(response.text)
