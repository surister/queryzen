from queryzen import Zen
from queryzen.sql import safe_sql_replace


def test_sql_replace():
    result = safe_sql_replace('SELECT * FROM products WHERE id = :val',
                              {'val': '10; DROP members--'})
    assert result == "SELECT * FROM products WHERE id = '10; DROP members--'"

    result = safe_sql_replace(':val, :val1, :val2',
                              {'val': 'val', 'val1': 1, 'val2': None})
    assert result == "'val', 1, NULL"


def test_sql_preview():
    zen = Zen.empty()
    zen.query = ':val, :val1, :val2'
    assert zen.preview(**{'val': 'val', 'val1': 1, 'val2': None}) == "'val', 1, NULL"
