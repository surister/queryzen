# pylint: disable=C0114


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
            replacement = 'NULL'

        else:
            raise ValueError(f'Unsupported parameter type: {type(value)}')

        placeholder = f':{key}'
        sql = sql.replace(placeholder, replacement)

    return sql
