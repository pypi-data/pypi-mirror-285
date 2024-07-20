from datetime import datetime
import os

from django.contrib import admin
from django.utils.timesince import timesince

from ..models import RequestException as Model


class ModelAdmin(admin.ModelAdmin):
    list_display = [
        # "request",
        "exc_class",
        "exc_message",
        "created_at",
        "time",
        "timesince",
    ]
    list_filter = [
        "exc_class",
    ]
    search_fields = [
        "url",
        "exc_class",
        "exc_message",
    ]

    def time(self, obj):
        return datetime.fromtimestamp(obj.created_at)

    def timesince(self, obj):
        return "%s ago" % timesince(datetime.fromtimestamp(obj.created_at))

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Model, ModelAdmin)
