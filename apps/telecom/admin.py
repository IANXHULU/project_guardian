from django.contrib import admin
from .models import TelecomCheck


@admin.register(TelecomCheck)
class TelecomCheckAdmin(admin.ModelAdmin):
    list_display = (
        "transaction",
        "check_type",
        "provider",
        "result",
        "score",
        "reference",
        "created_at",
    )

    search_fields = (
        "check_type",
        "provider",
        "reference",
    )

    list_filter = (
        "check_type",
        "provider",
        "result",
    )