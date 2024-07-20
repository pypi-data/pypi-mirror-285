from django.contrib import admin

from ..models import Config as Model

class ModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "query",
        "request_queue",
        "request_exception_queue",
        "response_queue",
        "restart_interval",
        "sleep_interval",
    ]

admin.site.register(Model, ModelAdmin)
