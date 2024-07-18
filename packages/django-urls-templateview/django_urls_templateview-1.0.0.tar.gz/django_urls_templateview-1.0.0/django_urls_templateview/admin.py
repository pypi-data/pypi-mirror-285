from django.contrib import admin

from .models import Map as Model


class ModelAdmin(admin.ModelAdmin):
    search_fields = [
        "url",
        "template_name",
    ]


admin.site.register(Model, ModelAdmin)
