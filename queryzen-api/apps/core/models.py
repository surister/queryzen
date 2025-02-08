# pylint: disable=C0114
from __future__ import annotations

from django.db import models
from django.db.models import QuerySet, Avg
from django.utils.translation import gettext_lazy as _

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

    @property
    def last_run(self) -> Execution:
        """Return last execution of the Zen."""
        return self.executions.order_by('-executed_at').first()

    @property
    def average_execution_time(self) -> float:
        return self.executions.aggregate(
            Avg('execution_time_in_ms')
        ).get('execution_time_in_ms__avg', 0)

    @property
    def failed_executions(self) -> int:
        return self.executions.filter(state=Execution.State.INVALID).count()

    class Meta:
        unique_together = ('collection', 'name', 'version')


class Execution(UUIDMixin):
    class State(models.TextChoices):
        VALID = 'VA', _('Valid')
        INVALID = 'IN', _('Invalid')

    state = models.CharField(max_length=2, choices=State.choices)
    executed_at = models.DateTimeField(auto_now_add=True)
    zen = models.ForeignKey(to=Zen, on_delete=models.CASCADE, related_name='executions')
    query = models.TextField()
    execution_time_in_ms = models.FloatField()
    error = models.TextField(null=True)
