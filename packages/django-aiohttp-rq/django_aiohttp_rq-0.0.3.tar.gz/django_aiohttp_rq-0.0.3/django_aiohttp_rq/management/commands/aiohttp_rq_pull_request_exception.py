import json

from django.core.management.base import BaseCommand

from aiohttp_rq.redis_client import REDIS, REQUEST_EXCEPTION_QUEUE as QUEUE
from ...models import Config, RequestException
from ..mixins import DebugMixin

CONFIG = Config.objects.all().first()
if not CONFIG:
    CONFIG,_ = Config.objects.get_or_create(id=1)
DB_TABLE = RequestException._meta.db_table
QUEUE = CONFIG.request_exception_queue
PREFETCH_COUNT = 10000


class Command(DebugMixin,BaseCommand):
    def handle(self, *args, **options):
        create_list = []
        pipe = REDIS.pipeline()
        pipe.lrange(QUEUE, 0, PREFETCH_COUNT - 1)  # Get msgs (w/o pop)
        pipe.ltrim(QUEUE, PREFETCH_COUNT, -1)  # Trim (pop) list to new value
        redis_value_list, trim_success = pipe.execute()
        if redis_value_list:
            count = len(redis_value_list)
            self.debug('PULL %s (%s)' % (QUEUE,count))
            for redis_value in redis_value_list:
                redis_data = json.loads(redis_value)
                create_list += [RequestException(
                    url=redis_data['url'],
                    exc_class=str(data['exc_class']),
                    exc_message=str(data['exc_message'])
                )]
            self.debug('BULK CREATE %s (%s)' % (DB_TABLE,count))
            RequestException.objects.bulk_create(create_list)
