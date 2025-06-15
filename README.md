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

## Quick example using our python library.

```python
from queryzen import QueryZen

qz = QueryZen()

zen = qz.create("mountain_summits", query="""
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
    LIMIT :limit
""")

result = qz.run(
    zen,
    database=crate,
    schema='sys',
    table_name='summits',
    country='AT',
    height=3000,
    orderby='height',
    limit=100
)
print(result.as_table())
# +---------+--------+---------------------+----------------------+
# | country | height | mountain            | coordinates          |
# +---------+--------+---------------------+----------------------+
# | AT      | 3798   | Großglockner        | [12.69444, 47.07417] |
# | AT      | 3770   | Wildspitze          | [10.86722, 46.88528] |
# | AT      | 3666   | Großvenediger       | [12.34639, 47.10917] |
# | AT      | 3564   | Großes Wiesbachhorn | [12.75528, 47.15639] |
# | AT      | 3550   | Großer Ramolkogel   | [10.95889, 46.84667] |
# | AT      | 3540   | Schalfkogel         | [10.95917, 46.80167] |
# | AT      | 3535   | Hochvernagtspitze   | [10.79611, 46.88139] |
# | AT      | 3533   | Watzespitze         | [10.79556, 46.98944] |
# | AT      | 3507   | Zuckerhütl          | [11.15389, 46.96444] |
# | AT      | 3497   | Schrankogel         | [11.09917, 47.04389] |
# +---------+--------+---------------------+----------------------+
```

## Quick example using HTTP.

### Create a Zen.

```sh
curl -X PUT https://your-queryzen-server.com/v1/collection/development/zen/summits \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
          "sql": "SELECT * FROM sys.summits WHERE height = :height and COUNTRY = :country
           "parameters": {
             "height": {
                  "type": "integer",
                  "default" 2500
             },
             "country": {
                 "type": "string",
                 "default": "AT"
             }
           }
         }'
```

### Run a Zen.

```sh
curl -X POST https://your-queryzen-server.com/v1/collection/development/zen/summits \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "parameters": {
             "database: "crate",
             "height": 1000,
             "country": "AT"
           }
         }'
```

# Why QueryZen & Use cases.

With QueryZen you can:

- Quickly create HTTP Rest endpoints of your SQL data.
- Integrate your SQL data in your data pipelines with minimal configuration.
- Monitor individual query executions and analyze metrics.
- Version your SQL queries, build and test queries without affecting production.
- Create materialized views for SQL databases that do not support them.
