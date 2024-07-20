__all__ = ["Config"]

from django.db import models


class Config(models.Model):
    id = models.BigAutoField(primary_key=True)
    request_queue = models.CharField(default='aiohttp_rq_request',max_length=256,help_text='Redis request queue')
    request_exception_queue = models.CharField(default='aiohttp_rq_request_exception',max_length=256,help_text='Redis request exception queue')
    response_queue = models.CharField(default='aiohttp_rq_response',max_length=256,help_text='Redis response queue')
    query = models.TextField(null=True,help_text='worker SQL query')
    restart_interval = models.IntegerField(null=True,help_text='worker restart interval')
    sleep_interval = models.FloatField(default=0.1,help_text='worker sleep interval')

    class Meta:
        db_table = 'aiohttp_rq_config'
