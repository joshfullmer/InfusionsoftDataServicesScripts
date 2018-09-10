from django.db import models


class Instance(models.Model):
    name = models.CharField(max_length=30)
    api_key = models.CharField(max_length=100, blank=True)
    access_token = models.CharField(max_length=50, blank=True)
    refresh_token = models.CharField(max_length=50, blank=True)
    expire_time = models.DateTimeField(blank=True)
