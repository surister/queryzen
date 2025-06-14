# In depth: Creating a Zen.

!!! Note
    The snippets of this page assumes you have imported
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

This will create a Zen with name `"myzen"` and the collection `"main"`. If you run it again, it will create
a new version of the query. The default is `AUTO`, this means that the backend will automatically
handle versioning, they are monotonically increasing integers.

You can change the query and descriptions on new versions to reflect the evolution of your query.

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

A collection is a namespace to group your zens. The default collection is `"main"`.

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
a query in a the default collection

```python
zen = qz.create('myzen', query='select 1')

# ok
```

it will not collide.

## Specifying a version

By default, the backend automatically handles Zen versioning; nonetheless
you can specify a version:

```python
zen = qz.create('myzen', query='select 2', version=10)

# Zen(id='8a839a35-46e2-4ebd-af07-4c1a381d99d2',
#     name='myzen',
#     version=10,
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

If you create a Zen specifying a version, and then create a version with `AUTO` version (the
default)
the latest value will be picked to add +1.

```python
qz.create('myzen', query='select 2')  # Will create version 1 if it does not exist
qz.create('myzen', query='select 2', version=5)  # creates version 5
zen = qz.create('myzen', query='select 2')  # creates version 5+1 = 6

# Zen(id='45da71b2-761d-4fac-a2c7-9ef5c0a6353a',
#     name='myzen',
#     version=6,
#     query='select 2',
#     description=None,
#     created_at='2025-03-02T12:13:47.229631Z',
#     default_parameters=None,
#     collection='main',
#     created_by='not_implemented',
#     state='UN',
#     executions=[])
```


## 
