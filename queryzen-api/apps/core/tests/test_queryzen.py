# pylint: disable=C0114
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from apps.core.models import Zen
from apps.core.tests.factories import QueryZenFactory


class QueryZenTestCase(TestCase):
    """Django tests for QueryZen"""
    def setUp(self) -> None:
        # Populate testing db with some zens
        self.zens = [QueryZenFactory.create() for _ in range(10)]

    def test_list_all_zen(self):
        """
        Request all zens
        """
        url = reverse('zens-list')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data is not None
        assert len(response.data) == len(self.zens)

    def test_list_all_zen_with_filters(self):
        """
        Request zens with applying filters
        """

        q: Zen = QueryZenFactory.create(
            collection='test',
            name='testing_zen',
        )

        filter_through_collection = f'{reverse('zens-list')}?collection={q.collection}'

        response = self.client.get(filter_through_collection)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        filter_through_version = (f'{reverse('zens-list')}?version={q.version}'
                                  f'&collection={q.collection}&name={q.name}')

        response = self.client.get(filter_through_version)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        filter_through_name = f'{reverse('zens-list')}?name={q.name}'

        response = self.client.get(filter_through_name)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_all_collections(self):
        """
        Request all collections
        """
        QueryZenFactory.create(
            collection='test',
        )
        url = reverse('collections-list')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data is not None

        assert len(response.data) == 2

    def test_list_all_zens_within_collection(self):
        """
        Retrieve all zens within collection
        """
        url = reverse('collections-detail', args=[self.zens[0].collection])
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data is not None
        assert len(response.data) == len(self.zens)

    def test_all_zens_given_collection_and_name(self):
        """
        Retrieve all zens given collection and name
        """
        q = QueryZenFactory.create(
            name='testing_zen',
        )
        QueryZenFactory.create(
            name='testing_zen',
        )
        url = reverse('collections-zen', args=[q.collection, q.name])

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data is not None
        assert len(response.data) == 2

    def test_create_zen(self):
        """
        Create a new zen
        """
        payload = {
            'query': 'SELECT * from testing_zen',
            'description': 'testing_zen',
        }

        collection = 'testing'
        name = 'testing_zen'

        url = reverse('collections-zen', args=[collection, name])

        zens_before = Zen.objects.count()
        response = self.client.put(url, payload, content_type='application/json')
        zens_after = Zen.objects.count()

        zen = Zen.objects.get(pk=response.data.get('id'))

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data is not None
        assert zens_after == zens_before + 1
        assert zen.name == name
        assert zen.collection == collection

    def test_create_new_queryzen_will_increase_version(self):
        """
        When a new queryzen is created with the same name and collection than a previous one,
        it will increase the version + 1.
        """
        q = QueryZenFactory.create(
            name='testing_zen',  # default collection is main
        )

        payload = {
            'query': 'SELECT * from testing_zen WHERE test > :param',
            'description': 'testing_zen',
        }

        url = reverse('collections-zen', args=[q.collection, q.name])

        zens_before = Zen.objects.count()
        response = self.client.put(url, payload, content_type='application/json')
        zens_after = Zen.objects.count()

        zen = Zen.objects.get(pk=response.data.get('id'))

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data is not None
        assert zens_after == zens_before + 1
        assert zen.version == q.version + 1

    def test_delete_zen(self):
        """
        Delete an existing zen
        """

        zen_to_delete: Zen = QueryZenFactory.create(name='deleting_zen')

        url = reverse('collections-zen',
                      args=[zen_to_delete.collection, zen_to_delete.name]
        )

        zens_before = Zen.objects.count()
        response = self.client.delete(url,
                                      {'version': zen_to_delete.version},
                                      content_type='application/json')
        zens_after = Zen.objects.count()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
        assert zens_after == zens_before - 1
