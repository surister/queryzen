# In depth: Running a Zen.

!!! Note
    The snippets of this page assumes you have imported
    ```python
    from queryzen import QueryZen

    qz = QueryZen()
    ```

## Running a Zen

To run a zen, get a `Zen` object, and pass it to `.run`, to get a zen you can use `get_or_create`, `create`, and `get`.

```python
zen = qz.get_or_create('demo_query', 'select 1 as n')
result = qz.run(zen)
print(result.as_table())
# +---+
# | n |
# +---+
# | 1 |
# +---+
```

## Running a Zen with Parameters

### Parametrizing

To add a parameter to a query, add the ':' character following a name, example:

```sql
select :number as :column_name
```

```python
qz.create('demo_query', query='select :number as :column_name')
```

```python

```