FROM python:3.12

WORKDIR app/

RUN pip install poetry

COPY pyproject.toml .

RUN poetry install

COPY . .
