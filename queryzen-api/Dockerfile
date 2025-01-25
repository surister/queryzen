FROM python:3.12

RUN pip install poetry

COPY pyproject.toml .

RUN poetry install

COPY . .

RUN poetry run python manage.py migrate

CMD ["poetry", "run","python", "manage.py", "runserver", "0.0.0.0:8000"]