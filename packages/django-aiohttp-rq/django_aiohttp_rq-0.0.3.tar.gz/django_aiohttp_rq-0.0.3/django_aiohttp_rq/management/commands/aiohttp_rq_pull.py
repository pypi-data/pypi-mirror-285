from django.core.management import call_command
from django.core.management.base import BaseCommand

COMMAND_LIST = [
    'aiohttp_rq_pull_request_exception',
    'aiohttp_rq_pull_response'
]

class Command(BaseCommand):
    def handle(self, *args, **options):
        for command in COMMAND_LIST:
            call_command(command)
