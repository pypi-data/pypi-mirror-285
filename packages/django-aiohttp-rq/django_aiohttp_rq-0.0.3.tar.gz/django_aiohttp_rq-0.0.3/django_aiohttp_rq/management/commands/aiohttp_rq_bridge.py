import logging
import sys
import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

from ...models import Config
from ..mixins import DebugMixin

CONFIG = Config.objects.all().first()
if not CONFIG:
    CONFIG,_ = Config.objects.get_or_create(id=1)
RESTART_AT = None
if CONFIG.restart_interval:
    RESTART_AT = time.time()+CONFIG.restart_interval
STARTED_AT = time.time()

class Command(DebugMixin,BaseCommand):

    def handle(self, *args, **options):
        if not CONFIG.query:
            self.debug('NULL QUERY')
        while not RESTART_AT or time.time()<RESTART_AT:
            try:
                if CONFIG.query:
                    cursor = connection.cursor()
                if CONFIG.query:
                    self.debug(CONFIG.query)
                    cursor.execute(CONFIG.query)
                call_command('aiohttp_rq_pull')
                call_command('aiohttp_rq_push')
                time.sleep(CONFIG.sleep_interval)
            except Exception as e:
                logging.error(e)
                if STARTED_AT+30>time.time():
                    time.sleep(10) # slowdown restarts/logging spam
                sys.exit(1)
