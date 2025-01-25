from django.db import models
from django.utils import timezone


class QueryLambda(models.Model):
    name = models.CharField(max_length=256)
    query = models.TextField()
    version = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'version',)

    @property
    def latest_version(self):
        return QueryLambda.objects.filter(name=self.name).order_by('-created_at').first()