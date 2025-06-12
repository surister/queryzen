# QueryZen - SQL over HTTP made easy.
[![📝🐍 Integration tests - master](https://github.com/surister/queryzen/actions/workflows/client_test.yml/badge.svg)](https://github.com/surister/queryzen/actions/workflows/client_test.yml)
[![.github/workflows/release.yml](https://github.com/surister/queryzen/actions/workflows/release.yml/badge.svg)](https://github.com/surister/queryzen/actions/workflows/release.yml)
![PyPI - Status](https://img.shields.io/pypi/status/queryzen)

[![Quality Gate Status](https://sonar.pyramidops.com/api/project_badges/measure?project=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1&metric=alert_status&token=sqb_a2b02087bce2cb15b3cc68c0d4c03243da867f08)](https://sonar.pyramidops.com/dashboard?id=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1)
[![Security Hotspots](https://sonar.pyramidops.com/api/project_badges/measure?project=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1&metric=security_hotspots&token=sqb_a2b02087bce2cb15b3cc68c0d4c03243da867f08)](https://sonar.pyramidops.com/dashboard?id=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1)
[![Vulnerabilities](https://sonar.pyramidops.com/api/project_badges/measure?project=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1&metric=vulnerabilities&token=sqb_a2b02087bce2cb15b3cc68c0d4c03243da867f08)](https://sonar.pyramidops.com/dashboard?id=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1)
[![Code Smells](https://sonar.pyramidops.com/api/project_badges/measure?project=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1&metric=code_smells&token=sqb_a2b02087bce2cb15b3cc68c0d4c03243da867f08)](https://sonar.pyramidops.com/dashboard?id=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1)
[![Maintainability Rating](https://sonar.pyramidops.com/api/project_badges/measure?project=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1&metric=sqale_rating&token=sqb_a2b02087bce2cb15b3cc68c0d4c03243da867f08)](https://sonar.pyramidops.com/dashboard?id=surister_queryzen_c0946901-04b6-4415-85f3-a9b95135b8e1)


QueryZen allows you to create and run Zens, a `Zen` is a named, parameterized and versioned SQL 
query that is run over HTTP REST endpoints.

The project ships several components, these components can be easily extended or improved; everything
is open-source under MIT license.

## QueryZen ships:

* HTTP REST backend to handle the lifetime of Zens. Made in Django.
* Task execution backend to handle the execution of the `Zens`. Made in Celery.
* Pythonic package to programmatically use QueryZen. Made in Python.
* A Database driver abstraction layer for SQL Drivers. Made in Python.

## Feature Overview:
* Create, get and delete `Zens` in different collections and run them in different Databases.
* Automatically version queries, name and safely parametrize queries with special functions.
* High level of Coverage and Tests.
* Track, save and analyze statistics of your queries over time and versions.
* Everything is dockerized for easy development and deployment.

## Quick Overview
With QueryZen backend deployed in `localhost:8000`, we can start using `Zens` with our Python
package:
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
