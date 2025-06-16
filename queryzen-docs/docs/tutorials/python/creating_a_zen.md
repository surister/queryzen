# Creating a Zen

!!! Note
    The snippets of this page assumes you have imported queryzen.
    ```python
    from queryzen import QueryZen

    qz = QueryZen()
    ```
    

The simplest way to create a Zen is:

```python
zen = qz.create('myzen', query='select 1')

# Zen(id='d32241d2-0845-4d9d-a037-786dfa7ba682',
#     name='myzen',
#     version=1,
#     query='select 1',
#     description=None,
#     created_at='2025-03-02T11:59:07.110211Z',
#     default_parameters=None,
#     collection='main',
#     created_by='not_implemented',
#     state='UN',
#     executions=[])
```

This will create a Zen with name `myzen` and the default collection `main`. 
If you another zen with the same name, it will create a new version of the zen, that is, if you don't specify a version.

The default version is `AUTO`, this means that the backend will automatically handle versioning,
they’re monotonically increasing integers.

You can change the query, descriptions and default parameters values on new versions 
to reflect the evolution of your query.

```python
zen = qz.create('myzen', query='select 2')

# Zen(id='d32241d2-0845-4d9d-a037-786dfa7ba682',
#     name='myzen',
#     version=2, <--------------------
#     query='select 2', <--------------------
#     description=None,
#     created_at='2025-03-02T11:59:07.110211Z',
#     default_parameters=None,
#     collection='main',
#     created_by='not_implemented',
#     state='UN',
#     executions=[])
```

## Collections

A collection is a namespace to group your zens. The default collection is `main`.

You can specify in which collection you want your zen to be created:

```python
zen = qz.create('myzen', collection='development', query='select 1')

# Zen(id='b6af1dee-4816-4a3e-8246-d187eb82a1c5',
#     name='myzen',
#     version=1,
#     query='select 1',
#     description=None,
#     created_at='2025-03-02T12:21:41.947371Z',
#     default_parameters=None,
#     collection='development',
#     created_by='not_implemented',
#     state='UN',
#     executions=[])
```

Now there is a Zen named `myzen` in collection `development`, if we now create
a query in a the default collection it will not collide.

```python
zen = qz.create('myzen', query='select 1')
```

## Specifying a version

By default, the backend automatically handles Zen versioning; nonetheless, 
you can specify a version:

```python
zen = qz.create('myzen', query='select 2', version=10)

# Zen(id='8a839a35-46e2-4ebd-af07-4c1a381d99d2',
#     name='myzen',
#     version=10, <---------------
#     query='select 1',
#     description=None,
#     created_at='2025-03-02T12:05:13.690029Z',
#     default_parameters=None,
#     collection='main',
#     created_by='not_implemented',
#     state='UN',
#     executions=[])
```

If you try to create a version that already exists, an error will be raised:

```python
zen = qz.create('myzen', query='select 2', version=10)
# ...
#     raise ZenAlreadyExistsError()
# queryzen.exceptions.ZenAlreadyExistsError
```

If you create a zen specifying a version, and then create a version with AUTO version the latest value
will be used to create the new version (by incrementing it.)

```python
qz.create('myzen', query='select 2')  # version 1
qz.create('myzen', query='select 2', version=5)  # version 5
zen = qz.create('myzen', query='select 2')  # version 5+1 = 6

# Zen(id='45da71b2-761d-4fac-a2c7-9ef5c0a6353a',
#     name='myzen',
#     version=6, <-----------------
#     query='select 2',
#     description=None,
#     created_at='2025-03-02T12:13:47.229631Z',
#     default_parameters=None,
#     collection='main',
#     created_by='not_implemented',
#     state='UN',
#     executions=[])
```

## Parametrizing a Zen

Zens are parametrized by writing a `:` character, following by the name of the parameter in the query.

Example:

```sql
zen = qz.create("""
    SELECT
      country,
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
    LIMIT 10
"""
)
```

This query has five parameters: `schema`, `table_name`, `country`, `height` and `orderby`

A zen can have no parameters.

`IDENT` is a special function that will convert the parameter to an `identifier`, it is designed
to be used when referencing schemas, table and column names. Different databases might use different
strategies.

todo: see running a zen with parameters.

## Default parameter values

A parameter can be given a default value. The default value will be used when running the query
if a new value is not provided.

```python
zen = qz.create(
    "zen_with_default",
    query="select :some_value",
    default={'some_value': 1}
)
```

Preferably, pass a `Default` object.


```python
from queryzen import Default

zen = qz.create(
    "zen_with_default",
    query="select :some_value",
    default=Default(some_value=1)
)
```

If a passed default parameter doesn’t exist in the query, an exception will be raised.

```python
zen = qz.create(
    "zen_with_default",
    query="select :some_value",
    default=Default(some_value=1, extra_param='job')
)
#    raise DefaultValueDoesNotExistError(f'default received a parameter'
#queryzen.exceptions.DefaultValueDoesNotExistError: default received a parameter that is not in the query: 'extra_param'
```

