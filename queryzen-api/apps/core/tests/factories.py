"""Faker Factories for QueryZen, used to generate fake data."""
from factory import LazyAttribute
from factory.django import DjangoModelFactory

from faker import Faker

from apps.core.models import Zen

fake = Faker()


class QueryZenFactory(DjangoModelFactory):
    collection = LazyAttribute(lambda o: 'main')

    class Meta:
        model = Zen
