# Getting started
[![PyPI - Version](https://img.shields.io/pypi/v/queryzen)](https://pypi.org/project/queryzen/)

`QueryZen` ships a complete Python library to use and manage your Zens.


## Installation

pipx

```shell
pipx install queryzen
```

poetry

```shell
poetry add queryzen
```

uv

```shell
uv add queryzen
```

!!! Important

    The queryzen package connects to the QueryZen backend, see [todo add link] on how to quickly
    get started.

## Specify backend url

```python
import os
os.environ['QUERYZEN_API_URL'] = 'https://yourqueryzenapi:8499'
```

By default it uses `'http://localhost:8000'`.

See [todo add link] for more constants.

## Creating a Zen.

```python
from queryzen import QueryZen

qz = QueryZen()

qz.create(collection='prod',
          name='myzen',
          query='select * from tbl1 where val > :val')
```

## Getting a Zen.

```python
from queryzen import QueryZen

qz = QueryZen()

zen = qz.get('myzen', collection='prod')
```

## Running a Zen.

```python
from queryzen import QueryZen

qz = QueryZen()

zen = qz.get('myzen', collection='prod')

result = qz.run(zen, val=123)
```

## Deleting a Zen.

```python
from queryzen import QueryZen

qz = QueryZen()

zen = qz.get('myzen', collection='prod')

qz.delete(zen)
```