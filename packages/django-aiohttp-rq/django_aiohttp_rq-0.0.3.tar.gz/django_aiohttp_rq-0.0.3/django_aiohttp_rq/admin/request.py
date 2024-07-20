from django.contrib import admin

from ..models import Request as Model

class ModelAdmin(admin.ModelAdmin):
    search_fields = [
        "url",
        "method",
    ]

admin.site.register(Model, ModelAdmin)
