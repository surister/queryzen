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

        return columns, rows
