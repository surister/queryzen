# QueryZen - SQL over HTTP made easy.
[![📝🐍 Integration tests - master](https://github.com/surister/queryzen/actions/workflows/client_test.yml/badge.svg)](https://github.com/surister/queryzen/actions/workflows/client_test.yml)
[![.github/workflows/release.yml](https://github.com/surister/queryzen/actions/workflows/release.yml/badge.svg)](https://github.com/surister/queryzen/actions/workflows/release.yml)
![PyPI - Status](https://img.shields.io/pypi/status/queryzen)

A `Zen` is a named, parameterized and versioned SQL query that is created, updated and executed
over HTTP endpoints.

It allows you to decouple SQL from your application. Controlling, versioning
and securing your data access from development to production.

QueryZen ships:

- HTTP REST backend to handle the lifetime of Zens.
- Task execution backend to handle the execution of the queries.
- Database driver abstraction for Python SQL drivers.
- Pythonic package to programmatically use QueryZen.

We also ship testing and production docker-composes to streamline development and deployment.

For more information, see:

* [Project repository](https://github.com/surister/queryzen)
* [Documentation]()
* [How to contribute]()
* [License](./LICENSE.md)

# Why QueryZen & Use cases.

With QueryZen you can:

- Quickly create HTTP Rest endpoints of your SQL data.
- Integrate your SQL data in your data pipelines with minimal configuration.
- Monitor individual query executions and analyze metrics.
- Version your SQL queries, build and test queries without affecting production.
- Create materialized views for SQL databases that do not support them.

Feature Overview:
    * Create, get and delete Zens in different collections and run them in different Databases.
    * Automatically version queries, name and safely parametrize queries with special functions.
    * High level of Coverage and Tests.
    * Track, save and analyze statistics of your queries over time and versions.
    * Everything is dockerized for easy development and deployment.

## Quick Overview

With QueryZen backend deployed in `localhost:8000`, we can start using `Zens` with our Python
package.

```python
from queryzen import QueryZen

qz = QueryZen()

query = """
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
# Creates a Zen with name 'mountains'
zen = qz.create('mountains', query=query)

# Create a Zen with parameters.
result = qz.run(zen,
                database='crate',  # We support multi-database access.
                schema='sys',
                table_name='summits',
                country='CH',
                height=2000,
                orderby='height')
print(result)
#ZenExecution(id='5b2144b5-d7f8-45e5-988b-94200f082f3a', row_count=320, sta...

print(result.query)
# SELECT
#   country,
#   height,
#   mountain,
#   coordinates
# FROM
#   "sys"."summits"
# WHERE
#   country = 'CH'
#   and height >= 2000
# ORDER BY
#   'height'

print(result.as_table())
# +---------+--------+----------------+---------------------+
# | country | height | mountain       | coordinates         |
# +---------+--------+----------------+---------------------+
# | CH      | 4634   | Monte Rosa     | [7.86694, 45.93694] |
# | CH      | 4545   | Dom            | [7.85889, 46.09389] |
# | CH      | 4506   | Weisshorn      | [7.71583, 46.10139] |
# | CH      | 4357   | Dent Blanche   | [7.61194, 46.03417] |
# | CH      | 4314   | Grand Combin   | [7.29917, 45.9375]  |
# | CH      | 4274   | Finsteraarhorn | [8.12611, 46.53722] |
# | CH      | 4221   | Zinalrothorn   | [7.69028, 46.065]   |
# | CH      | 4206   | Alphubel       | [7.86389, 46.06306] |
# | CH      | 4199   | Rimpfischhorn  | [7.88417, 46.02333] |
# | CH      | 4193   | Aletschhorn    | [7.99389, 46.465]   |
# +---------+--------+----------------+---------------------+
```


## Learn more.
If this is your first time using QueryZen we recommend reading in this order:

1. `Concepts: Zen` - It explains what a Zen is, (a supercharged SQL query).
2. `Concepts: Queryzen` - It explains the architecture of the project and its components.

## Using QueryZen:

HTTP:

1. `Tutorials: Http` - It explains the HTTP Rest endpoints and functionalities.

Python:

1. `Tutorials: Python` - It explains the how to use the Python package.

For more advanced use cases see [TODO ADD LINK]
