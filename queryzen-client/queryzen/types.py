from typing import Literal

Column = str
Columns = list[Column]

Row = list | tuple
Rows = list[Row]

ColumnCenter = Literal["left", "center", "right"]


class _AUTO:
    def __repr__(self):
        return repr(str(self))

    def __str__(self):
        return 'latest'


AUTO = _AUTO()
