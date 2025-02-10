# pylint: disable=C0114
from __future__ import annotations

import re

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from apps.core.exceptions import MissingParametersError, ParametersMissmatchError
from apps.shared.mixins import UUIDMixin


class Zen(UUIDMixin):
    """A parametrized, versioned and named SQL query"""

    class State(models.TextChoices):
        VALID = 'VA', _('Valid')
        INVALID = 'IN', _('Invalid')
        UNKNOWN = 'UN', _('UNKNOWN')

    def save(self, *args, **kwargs):
        # self.version is either 'latest' or an integer.
        last_obj = self.latest.first()

        if last_obj:  # Check if last_obj exists
            if self.version == 'latest':
                self.version = last_obj.version + 1
        else:
            # First object, so the version starts at 1.
            self.version = 1
        super().save(*args, **kwargs)

    collection = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    description = models.TextField(null=True)
    query = models.TextField()
    default_parameters = models.JSONField(null=True)
    version = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=2, choices=State.choices, default=State.UNKNOWN)

    # TODO: Add created_by

    @property
    def latest(self) -> QuerySet:
        return Zen.objects.filter(name=self.name, collection=self.collection).order_by('-version')

    @classmethod
    def filter_by(cls, collection: str, name: str, version) -> QuerySet:
        """Filter the Zens given the collection name and version."""
        queryset = cls.objects.filter(collection=collection, name=name)
        if version == 'latest':
            queryset = queryset.order_by('-version')
        else:
            queryset = queryset.filter(version=version)
        return queryset

    def get_parameters(self, user_parameters: dict) -> dict:
        """Return the parameters that will be used from the addition
         of default_parameters + user_parameters.

         Default parameters will be updated with parameters given by the user, these parameters
         are not necessarily correct, as default parameters might not have all needed parameters.
         Validation is therefore needed afterwards.
         """
        parameters = self.default_parameters or dict()
        parameters.update(user_parameters)
        return parameters

    def validate_parameters(self, parameters: dict) -> None:
        """Validate that the given parameters are valid for the current query, right now
        valid means that they exist, there could be types mismatches that are dependent on the
        target Database.

        Args:
            parameters: The parameters to validate

        Raises:
            ParametersMissmatchError: If we receive parameters that are not in the query.
            MissingParametersError: If we still miss parameters after trying the default plus
            the received ones.
        """
        query_parameters = re.findall(r':(\w+)', self.query)

        if mismatch_parameters := set(parameters.keys()) - set(query_parameters):
            raise ParametersMissmatchError(
                f'Received parameter(s) that are not'
                f' used in the query: {list(mismatch_parameters)}')

        if missing_parameters := set(query_parameters) - set(parameters.keys()):
            raise MissingParametersError(f'The query is missing'
                                         f' parameter(s) to run: {list(missing_parameters)}')

    class Meta:
        unique_together = ('collection', 'name', 'version')


class Execution(UUIDMixin):
    """Represents the Execution of a Zen."""
    class State(models.TextChoices):
        VALID = 'VA', _('Valid')
        INVALID = 'IN', _('Invalid')

    state = models.CharField(max_length=2, choices=State.choices)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField()
    total_time = models.IntegerField()
    zen = models.ForeignKey(to=Zen, on_delete=models.CASCADE, related_name='executions')
    query = models.TextField()
    error = models.TextField()
    row_count = models.SmallIntegerField()
    parameters = models.TextField()
