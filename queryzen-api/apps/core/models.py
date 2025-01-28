from django.db import models

from apps.shared.mixins import UUIDMixin

from django.utils.translation import gettext_lazy as _


class QueryZen(UUIDMixin):
    class State(models.TextChoices):
        VALID = "VA", _("Valid")
        INVALID = "IN", _("Invalid")

    collection = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    description = models.TextField(null=True)
    query = models.TextField()
    version = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=2, choices=State.choices, default=State.VALID)

    # TODO: Add created_by

    class Meta:
        unique_together = ('name', 'version',)


class Execution(UUIDMixin):
    class State(models.TextChoices):
        VALID = "VA", _("Valid")
        INVALID = "IN", _("Invalid")

    state = models.CharField(max_length=2, choices=State.choices)
    executed_at = models.DateTimeField(auto_now_add=True)
    zen = models.ForeignKey(to=QueryZen, on_delete=models.CASCADE, related_name='executions')
