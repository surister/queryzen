from factory import LazyAttribute
from factory.django import DjangoModelFactory
import factory
from faker import Faker

from apps.core.models import QueryZen

fake = Faker()


class QueryZenFactory(DjangoModelFactory):
    collection = LazyAttribute(lambda o: 'main')

    class Meta:
        model = QueryZen
        django_get_or_create = ('name', 'version')

    name = factory.Sequence(lambda n: f'Zen{n}')
    version = factory.LazyAttribute(lambda _: fake.word())
