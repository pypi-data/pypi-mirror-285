__all__ = [
    "RequestException",
]

from django.db import models

from .utils import get_timestamp

class RequestException(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255)
    exc_class = models.TextField()
    exc_message = models.TextField()
    created_at = models.FloatField(default=get_timestamp)

    class Meta:
        db_table = 'aiohttp_rq_request_exception'
