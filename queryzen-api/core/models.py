from django.db import models


class Query(models.Model):
    name = models.CharField(primary_key=True, max_length=256)
    query = models.TextField()
    version = models.TextField()
