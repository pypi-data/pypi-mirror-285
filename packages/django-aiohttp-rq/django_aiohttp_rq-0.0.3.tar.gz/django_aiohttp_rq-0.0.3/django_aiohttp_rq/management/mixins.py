from django.conf import settings

class DebugMixin:
    def debug(self,message):
        if settings.DEBUG:
            self.stdout.write('DEBUG: %s\n' % message)
