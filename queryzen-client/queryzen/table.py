"""
Utilities to create Markdown tables.
"""
from .types import Columns, Rows, ColumnCenter


def center_string(string: str, pad_length: int, direction: ColumnCenter = "left") -> str:
    """
    Centers a `string` to a given `direction`

    Args:
        string: The string to center.
        pad_length: The other direction pad.
        direction: Where to pad the string to.

    Returns:
        The centered string.
    """
    if direction == "left":
        return string.ljust(pad_length)

    if direction == "right":
        return string.rjust(pad_length)

    return string.center(pad_length)


def make_table(columns: Columns, rows: Rows, column_center: ColumnCenter = "left"):
    """
    Creates a table with the given `columns` and `rows`, a column direction can be customized.

    Examples:
        >>> make_table(['a', 'b'], rows=[(1, 2), (3, 4)]) # ignore-doctest
        +---+---+
        | a | b |
        +---+---+
        | 1 | 2 |
        | 3 | 4 |
        +---+---+

        >>> make_table(['longercol1', 'longercol2'], rows=[(1, 2), (3, 4)], column_center='right')
        +------------+------------+
        | longercol1 | longercol2 |
        +------------+------------+
        |          1 |          2 |
        |          3 |          4 |
        +------------+------------+
    """
    # The width of every column, calculated as the max
    # length from the column name, or the biggest value.
    col_widths = []

    for i, column in enumerate(columns):
        # Get the biggest value (in character count) of the values from a given column.
        biggest_value_in_chars: int = 0
        for row in rows:
            # We assume that the index of the column in columns matches the row index inside rows.
            biggest_value_in_chars = max(len(str(row[i])), biggest_value_in_chars)

        col_widths.append(
            max(biggest_value_in_chars, len(column))
        )

    # Create separator
    separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"
    # Create header
    header = "| " + " | ".join(
        f"{center_string(col, col_widths[i], column_center)}" for i, col in
        enumerate(columns)) + " |"

    # Create rows
    row_lines = ["| " + " | ".join(
        f"{center_string(str(row[i]), col_widths[i], column_center)}" for i in
        range(len(columns))) + " |" for row in
                 rows]

    # Combine everything
    table = "\n".join(
        [
            separator,
            header,
            separator,
            *row_lines,
            separator
        ]
    )
    return table
