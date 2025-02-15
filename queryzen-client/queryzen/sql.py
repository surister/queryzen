# pylint: disable=C0114
import re


def parse_parameters(query: str, separator: str = ':') -> list[str]:
    return re.findall(rf'{separator}(\w+)', query)


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
