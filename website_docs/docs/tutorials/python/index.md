# Getting started
todo:
-- how to distinguish query execution from differnet bakcends

`QueryZen` ships a complete Python library to use and manage your Zens.

link: https://pypi.org/project/queryzen/

## Installation

pipx

```shell
pipx install queryzen
```

poetry

```shell
poetry add queryzen
```

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