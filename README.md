from apps.core.models import QueryZenfrom apps.core.models import QueryZenfrom apps.core.models import QueryZen

# queryzen

This is the canonical ``queryzen`` client (Python).d

* Features: 100% coverage and thorough testing.
* Compatability with backend is directly tested and can be enforced at runtime.
* Pythonic Ask for forgiveness (what were the initials?) and type safe API, checked with mypi.
* 100% use of docstrings and documentation [link documentation].

# Example

```python
from querzen import QueryZen

qz = QueryZen()

# Default collection is 'main' and version is 'latest'
some_zen = qz.create("my_zen", query='select * from sys.summits where country == :country and height > :height')
print(some_zen)

# Create a Zen that has two parameters, 'country' and 'height', the character ':' is used to specify parameters.
# if no default parameters are specified, they are m
zen = qz.create(
    name="mountains",
    collection="production",
    query="select * from sys.summits where country == :country and height > :height",
    default = {
        'country': 'United States',
        'height': 0
    },
    version=32,
    description="Gets all summits from a given country and height, defaults to all summits from United States",
)

print(zen == qz.get("mountains", collection="production")) # if no version is specified, it returns the created.
# True


# Run with default values.
result = qz.run(
    zen
) # Execution is blocked, it is run synchronously.

print(result.has_data)
print()

# Run with parameters.
result = qz.run(
    zen,
    country='Spain',
    height=1200
)

print(result.as_table())
print(zen.executions.oldest.as_table())

```

# API

Main classes are QueryZen, Zen and ZenExecutions.

```python
QueryZen.get
QueryZen.create
QueryZen.get_or_create
QueryZen.delete
QueryZen.list
```


