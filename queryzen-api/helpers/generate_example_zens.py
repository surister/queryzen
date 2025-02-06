"""
Script to generate zens for testing
"""
import os
import random

import django
from django.db import IntegrityError

from faker import Faker

from apps.core.models import Zen
from apps.core.tests.factories import QueryZenFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queryzen_api.settings')
django.setup()
fake = Faker()


def generate_random_sql():
    # Seleccionamos aleatoriamente el tipo de sentencia SQL
    sql_type = random.choice(['SELECT', 'INSERT', 'UPDATE'])

    if sql_type == 'SELECT':
        return generate_random_select()
    elif sql_type == 'INSERT':
        return generate_random_insert()
    elif sql_type == 'UPDATE':
        return generate_random_update()


def generate_random_select():
    table_name = fake.word()
    columns = [fake.word() for _ in range(random.randint(2, 5))]
    where_clause = generate_where_clause()

    sql = f'SELECT {', '.join(columns)} FROM {table_name}{where_clause};'
    return sql


def generate_random_insert():
    table_name = fake.word()
    columns = [fake.word() for _ in range(random.randint(2, 5))]
    param_names = [f':{col}' for col in columns]

    sql = f'INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(param_names)});'
    return sql


def generate_random_update():
    table_name = fake.word()
    columns = [fake.word() for _ in range(random.randint(2, 5))]
    set_clause = ', '.join([f'{col} = :{col}' for col in columns])
    where_clause = generate_where_clause()

    sql = f'UPDATE {table_name} SET {set_clause}{where_clause};'
    return sql


def generate_where_clause():
    # Generamos una cláusula WHERE aleatoria
    if random.choice([True, False]):  # 50% de probabilidad de tener un WHERE
        column = fake.word()
        param_name = f':{column}'
        operator = random.choice(['=', '<', '>', '<=', '>=', '!='])
        return f' WHERE {column} {operator} {param_name}'
    return ''


def generate_zens(entities):
    collections = [
        'main', 'testing', 'staging', 'production'
    ]
    query_names = [
        'mountain_filter', 'country_filter', 'state_filter'
    ]
    while Zen.objects.count() < entities:
        try:
            QueryZenFactory.create(
                collection=random.choice(collections),
                name=random.choice(query_names),
                description=fake.text(),
                query=generate_random_sql(),
                state=fake.random_element(Zen.State.values)
            )
        except IntegrityError:
            pass
    print(f'{entities} QueryZen entities have been created.')


if __name__ == '__main__':
    generate_zens(50)
