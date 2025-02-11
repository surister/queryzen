# pylint: disable=C0114
import re


def parse_parameters(query: str, separator: str = ':') -> list[str]:
    return re.findall(rf'{separator}(\w+)', query)


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
