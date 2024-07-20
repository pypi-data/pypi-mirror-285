__all__ = ["Request"]

from django.db import models


class Request(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.CharField(max_length=255)
    method = models.CharField(default="GET", max_length=255)
    data = models.TextField(null=True)
    headers = models.JSONField(null=True)
    allow_redirects = models.BooleanField(default=True)
    max_redirects = models.IntegerField(null=True, default=5)
    timeout = models.IntegerField(null=True)

    class Meta:
        db_table = 'aiohttp_rq_request'
