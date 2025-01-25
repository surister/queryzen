from django.db import models


class LambdaQuery(models.Model):
    name = models.CharField(max_length=256)
    query = models.TextField()
    version = models.TextField()

    class Meta:
        unique_together = ('name', 'version', )
