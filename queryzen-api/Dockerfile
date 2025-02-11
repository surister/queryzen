FROM python:3.12

WORKDIR queryzen-api/

RUN pip install poetry

COPY pyproject.toml .

# Use poetry to install packages only.
RUN poetry config virtualenvs.create false && poetry install
