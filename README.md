# QueryZen - SQL over HTTP made easy.

QueryZen allows you to create and run `Zens`, a `Zen` is a named, parameterized and versioned SQL query
that is run over HTTP REST endpoints. Decouple your SQL from you application, version it, 
and secure it from development to production.

QueryZen ships:
- HTTP REST backend to handle the lifetime of Zens.
- Task execution backend to handle the execution of the queries.
- Database driver abstraction for Python SQL drivers.
- Pythonic package to programmatically use QueryZen.

We also have a docker-compose to streamline development and deployment.

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
                 "default": "Canada"
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
             "height": 1000,
             "country": "Austria"
           }
         }'
```

## Quick example using our python library.

```python
...
```

# Why QueryZen & Use cases.
With QueryZen you can:
- Quickly create HTTP Rest endpoints of your SQL data.
- Integrate your SQL data in your data pipelines with minimal configuration.
- Monitor individual query executions and analyze metrics.
- Version your SQL queries, build and test queries without affecting production.
- Create materialized views for SQL databases that do not support them.

todo Add an example of each.


# Architecture overview
todo Explain architecture