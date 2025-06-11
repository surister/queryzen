# Run development setup:
The project is a monorepo of several subprojects: `queryzen-api` and `queryzen-client`, the easiest
way to work with it in Pycharm or Jetbrains-IDEs is to open every project separately.

To run the tests of queryzen-client, you need a working backend, some tests are unit, most are
integration.

We use [uv](https://github.com/astral-sh/uv), but other tools like pipx/pip could be used.

Follow the instructions in order to finally be able to run a full test suite, which
is also the correct environment to develop new features.

Clone the project:
```shell
git clone git@github.com:surister/queryzen.git
```
## Setup queryzen-api

Set up environment:
```shell
# Path: ./queryzen/queryzen-api
$ uv sync
```

Run django locally:
```shell
# Path: ./queryzen/queryzen-api
$ uv run python manage.py runsever
```

If it is the first time running, run the migrations:

```shell
# Path: ./queryzen/queryzen-api
$ uv run python managepy migrate
```

## Set up other backend apps
For local development, the django api is run locally as it needs changes quickly,
other components are more stale; those are run with a docker-compose.

```shell
# Path: ./queryzen/queryzen-api
docker compose -f docker-compose.yml up -d
```

## Set up queryzen-client

Set up environment:
```shell
# Path: ./queryzen/queryzen-client
$ uv sync
```

Run tests:
```shell
# Path: ./queryzen/queryzen-client
uv run pytest --cov=queryzen --cov-report html .
```

HTML with coverage will be created at `queryzen/queryzen-client/htmlcov`

Run lint:

```shell
# Path: ./queryzen/queryzen-client
uv run pylint .
```

## Running tests like the CI
Tests in CI are run using an overridden production template, to run that locally:

```shell
# Path: ./queryzen/queryzen-api
docker compose -f docker-compose-ci.yml -f docker-compose-ci.override.yml up -d --build
```

```shell
# Path: ./queryzen/queryzen-api
docker exec queryzen-api-django-1 bash -c "echo waiting 1s && sleep 1 && uv run python manage.py migrate"
```

```shell
# Path: ./queryzen/queryzen-api
docker exec queryzen-api-client-1 bash -c "echo waiting 1s && sleep 1 && uv run pytest --cov-report=term-missing:skip-covered --cov-report=xml:/tmp/coverage.xml --junitxml=/tmp/pytest.xml --cov=queryzen tests/" | tee /tmp/pytest-coverage.txt
```
