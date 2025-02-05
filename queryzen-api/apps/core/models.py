from __future__ import annotations

from django.db import models
from django.db.models import QuerySet

from apps.shared.mixins import UUIDMixin

from django.utils.translation import gettext_lazy as _


class QueryZen(UUIDMixin):
    class State(models.TextChoices):
        VALID = "VA", _("Valid")
        INVALID = "IN", _("Invalid")
        UNKNOWN = "UN", _("UNKNOWN")

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
        return QueryZen.objects.filter(name=self.name, collection=self.collection).order_by('-version')

    @classmethod
    def filter_by(cls, collection: str, name: str, version) -> QuerySet:
        """Filter the Zens given the collection name and version."""
        queryset = cls.objects.filter(collection=collection, name=name)
        if version == 'latest':
            queryset = queryset.order_by('-version')
        else:
            queryset = queryset.filter(version=version)
        return queryset

    class Meta:
        unique_together = ('collection', 'name', 'version')


class Execution(UUIDMixin):
    class State(models.TextChoices):
        VALID = "VA", _("Valid")
        INVALID = "IN", _("Invalid")

    state = models.CharField(max_length=2, choices=State.choices)
    executed_at = models.DateTimeField(auto_now_add=True)
    zen = models.ForeignKey(to=QueryZen, on_delete=models.CASCADE, related_name='executions')
    query = models.TextField()