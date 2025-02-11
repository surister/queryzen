FROM python:3.12

WORKDIR queryzen-client/

RUN pip install poetry

COPY . .

# Use poetry to install packages only.
RUN poetry config virtualenvs.create false && poetry install
