FROM python:3.12

WORKDIR app/

RUN pip install poetry

COPY pyproject.toml .

# Use poetry to install packages only.
RUN poetry config virtualenvs.create false
RUN poetry install
