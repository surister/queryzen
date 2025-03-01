FROM docker.io/python:3.12.9-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL author = github.com/surister

ARG BUILD_ENVIRONMENT=development
ARG APP_HOME=/app

ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

COPY . .

RUN uv sync