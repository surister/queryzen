# Running a Zen.

!!! Note
    The snippets of this page assumes you have imported
    ```python
    from queryzen import QueryZen

    qz = QueryZen()
    ```

## Running a Zen

To run a zen, get a `Zen` object, and pass it to `QueryZen.run`.

To get a zen you can use
`get_or_create`, `create`, and `get`.

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

Additionally, it also accepts `database` and `timeout`

```python
result = qz.run(zen, database='mysqldb1', timeout=1)
```

`database` has to be defined in your queryzen deployment.

[//]: # (TODO: See deploying a queryzen)

## Running a Zen with Parameters

Given the following Zen, with parameters `first_parameter`, `second_parameter` and `third_parameter`
where `third_parameter` has the default value of `"mycol"`.


```python
demo_zen = qz.create(
    'demo',
    query='select :first_parameter, :second_parameter as :third_parameter',
    default=Default(third_parameter='mycol')
)
```

Running the Zen providing all parameters:
```python
qz.run(
    demo_zen,
    first_parameter=1,
    second_parameter=2,
    third_pameter='someparameter'
)
```

If a parameter without a default value is missing, an exception will be raised:

```python
qz.run(
    demo_zen,
    first_parameter=1,
    third_pameter='someparameter'
)
#     raise MissingParametersError(response.error)
# queryzen.exceptions.MissingParametersError: The query is missing parameter(s) to run: ['second_parameter']
```

If the parameter has a default value, it is ok to not provide it.

```python
qz.run(
    demo_zen,
    first_parameter=1,
    second_parameter=2
)
```
## Zen execution results

Executions are wrapped in an object with a lot of information:

```python
import pprint

zen = qz.create(
    "mountain_summits",
    query="""
        SELECT country,
               height,
               mountain,
               coordinates
        FROM
            IDENT(:schema).IDENT(:table_name)
        WHERE
            country = :country
            and height >= :height
        ORDER BY
            :orderby
        LIMIT :limit
        """
)

result = qz.run(
    zen,
    database='crate',
    schema='sys',
    table_name='summits',
    country='AT',
    height=3000,
    orderby='height',
    limit=10
)

pprint.pprint(result)

# ZenExecution(id='7a44ba7c-075c-4441-b686-3c8143cf0e8a',
#              row_count=10,
#              state='VA',
#              started_at='2025-06-15T09:51:29.903368Z',
#              finished_at='2025-06-15T09:51:29.895823Z',
#              total_time=18,
#              query='SELECT country,\n'
#                    '                             height,\n'
#                    '                             mountain,\n'
#                    '                             coordinates\n'
#                    '                      FROM\n'
#                    '                          "sys"."summits"\n'
#                    '                      WHERE\n'
#                    "                          country = 'AT'\n"
#                    '                        and height >= 3000\n'
#                    '                      ORDER BY\n'
#                    "                          'height'\n"
#                    '                      LIMIT 10',
#              error='',
#              parameters={'country': 'AT',
#                          'height': 3000,
#                          'limit': 10,
#                          'orderby': 'height',
#                          'schema': 'sys',
#                          'table_name': 'summits'},
#              columns=['country', 'height', 'mountain', 'coordinates'])
```

We keep metadata of all query executions, you can access it in `zen.executions`.
