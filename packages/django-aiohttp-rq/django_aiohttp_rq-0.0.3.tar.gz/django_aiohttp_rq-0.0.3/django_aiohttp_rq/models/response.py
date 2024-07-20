__all__ = [
    "Response",
]

import json
import os

from django.db import models

from .utils import get_timestamp

class Response(models.Model):
    id = models.BigAutoField(primary_key=True)
    request = models.JSONField()
    url = models.CharField(max_length=1024)
    status = models.IntegerField()
    headers = models.JSONField()
    content_path = models.CharField(max_length=255,null=True)
    created_at = models.FloatField(default=get_timestamp)

    class Meta:
        db_table = 'aiohttp_rq_response'
