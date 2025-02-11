"""Test for verion enforcement, logic is in queryzen.__init__"""
from queryzen import strtobool
import pytest

from queryzen.table import make_table


@pytest.mark.parametrize("input_val, expected", [
    ("y", True), ("yes", True), ("t", True), ("true", True), ("on", True), ("1", True),
    ("n", False), ("no", False), ("f", False), ("false", False), ("off", False), ("0", False),
    ("Y", True), ("YES", True), ("T", True), ("TRUE", True), ("ON", True), ("1", True),
    ("N", False), ("NO", False), ("F", False), ("FALSE", False), ("OFF", False), ("0", False),
    (True, True), (False, False)
])
def test_strtobool_valid(input_val, expected):
    assert strtobool(input_val) == expected


@pytest.mark.parametrize("invalid_input", [
    "maybe", "2", "random", "", "truefalse"
])
def test_strtobool_invalid(invalid_input):
    with pytest.raises(ValueError):
        strtobool(invalid_input)


@pytest.mark.parametrize("invalid_input", [
    None, [], {}, 3.14
])
def test_strtobool_type_error(invalid_input):
    with pytest.raises(TypeError):
        strtobool(invalid_input)


def test_make_table():
    expected = """+------------+------------+
| longercol1 | longercol2 |
+------------+------------+
|          1 |          2 |
|          3 |          4 |
+------------+------------+"""
    result = make_table(['longercol1', 'longercol2'],
                        rows=[(1, 2), (3, 4)],
                        column_center='right')

    assert result == expected

    expected = """+------------+------------+
| longercol1 | longercol2 |
+------------+------------+
|     1      |     2      |
|     3      |     4      |
+------------+------------+"""
    result = make_table(['longercol1', 'longercol2'],
                        rows=[(1, 2), (3, 4)],
                        column_center='center')

    assert result == expected

    expected = """+------------+------------+
| longercol1 | longercol2 |
+------------+------------+
| 1          | 2          |
| 3          | 4          |
+------------+------------+"""
    result = make_table(['longercol1', 'longercol2'],
                        rows=[(1, 2), (3, 4)],
                        column_center='left')
    assert result == expected