"""
Types for our typing needs, we aim to be 100% type safe and enforce correctness with mypi.
"""

from typing import Literal

Column = str
Columns = list[Column]

Row = list | tuple
Rows = list[Row]

ZenState = Literal['valid', 'invalid', 'unknown']
ColumnCenter = Literal['left', 'center', 'right']


class Default:
    """Represents a Default values to be sent to QueryZen at creation time.

    Examples:
        >>> Default(param1=2, param2=3, some_value='test').to_dict()
        {'param1': 2, 'param2': 3, 'some_value': 'test'}


    """
    def __init__(self, **kwargs):
        self.values = []
        self._dict_to_typed_tuples(kwargs)

    def _dict_to_typed_tuples(self, mapping: dict):
        # We are internally storing the type of the value, we dont use this, probably need
        # to change this imp detail. fixme
        for k, v in mapping.items():
            self.values.append((k, type(v).__name__, v))

    def is_missing(self, parameters: list[str]) -> (bool, str):
        """Check if the given the Default parameters are in the given `parameters`, it will return
        a (result, missing_parameter) tuple.

        Args:
            parameters: The parameters to check.

        Examples:
            >>> Default(one=1, two=2).is_missing(['one'])
            (True, ['two'])

            >>> Default(one=1, two=2).is_missing(['one', 'two'])
            (False, [])
        """
        for p in self.values:
            if not p[0] in parameters:
                return False, p[0]
        return True, None

    def to_dict(self):
        d_out = {}
        for v in self.values:
            d_out[v[0]] = v[2]
        return d_out

    def __str__(self):
        names = ', '.join(list(f'{value}' for value in self.values))
        return f'{self.__class__.__qualname__}({names})'


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
