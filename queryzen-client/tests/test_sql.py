import pytest

from queryzen import Zen
from queryzen.sql import safe_sql_replace


def test_sql_replaces_raises():
    with pytest.raises(ValueError):
        safe_sql_replace("select :v", {'v': object})


def test_sql_replace_values():
    result = safe_sql_replace('SELECT * FROM products WHERE id = :val',
                              {'val': '10; DROP members--'})
    assert result == "SELECT * FROM products WHERE id = '10; DROP members--'"

    result = safe_sql_replace(':val, :val1, :val2',
                              {'val': 'val', 'val1': 1, 'val2': None})
    assert result == "'val', 1, NULL"


def test_sql_replace_ident():
    """Test that sql method properly replaces IDENT special function"""
    query = "select IDENT(:one), IDENT(:two) + :val from t"
    result = safe_sql_replace(query,
                              {'one': 'first_column',
                               'two': 'second_column',
                               'val': 'value'})

    assert result == """select "first_column", "second_column" + 'value' from t"""


def test_sql_preview():
    """Test Zen.preview method"""
    zen = Zen.empty()
    zen.query = ':val, :val1, :val2'
    assert zen.preview(**{'val': 'val', 'val1': 1, 'val2': None}) == "'val', 1, NULL"
