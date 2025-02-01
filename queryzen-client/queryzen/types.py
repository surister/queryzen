"""
Types for our typing needs, we aim to be 100% type safe and enforce correctness with mypi.
"""

from typing import Literal

Column = str
Columns = list[Column]

Row = list | tuple
Rows = list[Row]

ColumnCenter = Literal['left', 'center', 'right']


class _AUTO:
    """
    Automatic id handled by queryzen backend.

    When creating a queryzen, an incremental integer will be used e.g. 1, 2, 3, 4, 5, 6...

    When getting a queryzen, the latest queryzen will be returned.
    """
    def __repr__(self):
        return repr(str(self))

    def __str__(self):
        return 'latest'


AUTO = _AUTO()
