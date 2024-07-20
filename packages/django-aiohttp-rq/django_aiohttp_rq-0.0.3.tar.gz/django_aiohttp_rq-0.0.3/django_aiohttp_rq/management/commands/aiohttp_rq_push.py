import json

from django.core.management.base import BaseCommand

from aiohttp_rq.redis_client import REDIS, REQUEST_QUEUE as QUEUE
from ...models import Config, Request
from ..mixins import DebugMixin


CONFIG = Config.objects.all().first()
if not CONFIG:
    CONFIG,_ = Config.objects.get_or_create(id=1)
DB_TABLE = Request._meta.db_table
QUEUE = CONFIG.request_queue

class Command(DebugMixin,BaseCommand):
    def handle(self, *args, **options):
        request_list = list(Request.objects.all())
        if request_list:
            count = len(request_list)
            data_list = []
            for request in request_list:
                data_list+=[dict(
                    id=request.id,
                    url=request.url,
                    method=request.method,
                    headers=request.headers,
                    data=request.data,
                    allow_redirects=request.allow_redirects
                )]
            self.debug('PUSH %s (%s)' % (QUEUE,count))
            pipe = REDIS.pipeline()
            for data in data_list:
                REDIS.lpush(QUEUE, json.dumps(data))
            pipe.execute()
            id_list = list(map(lambda r:r.id,request_list))
            Request.objects.filter(id__in=id_list).delete()
            self.debug('DELETE %s (%s)' % (DB_TABLE,count))
            Request.objects.all().delete()
