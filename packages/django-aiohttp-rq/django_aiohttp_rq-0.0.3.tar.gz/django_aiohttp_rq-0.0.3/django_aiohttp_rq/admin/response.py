from datetime import datetime
import os

from django.contrib import admin
from django.utils.timesince import timesince

from ..models import Response as Model


class ModelAdmin(admin.ModelAdmin):
    list_display = [
        # "request",
        "url",
        "status",
        "content_path",
        "created_at",
        "time",
        "timesince",
    ]
    search_fields = [
        "url",
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
