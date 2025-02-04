from __future__ import annotations

from django.db import models

from apps.shared.mixins import UUIDMixin

from django.utils.translation import gettext_lazy as _


class QueryZen(UUIDMixin):
    class State(models.TextChoices):
        VALID = "VA", _("Valid")
        INVALID = "IN", _("Invalid")

    def save(self, *args, **kwargs):
        self.version = 1  # The Default version is 1 in new instances.

        # If a new instance is being created, get the latest one and add one.
        if not self.pk:
            if last := self.latest.version:
                self.version = last + 1

        super().save(*args, **kwargs)

    collection = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    description = models.TextField(null=True)
    query = models.TextField()
    version = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=2, choices=State.choices, default=State.VALID)

    # TODO: Add created_by

    @property
    def latest(self) -> QueryZen:
        return QueryZen.objects.filter(name=self.name, collection=self.collection).order_by('-version').first()

    class Meta:
        unique_together = ('collection', 'name', 'version',)


class Execution(UUIDMixin):
    class State(models.TextChoices):
        VALID = "VA", _("Valid")
        INVALID = "IN", _("Invalid")

    state = models.CharField(max_length=2, choices=State.choices)
    executed_at = models.DateTimeField(auto_now_add=True)
    zen = models.ForeignKey(to=QueryZen, on_delete=models.CASCADE, related_name='executions')
