from django.contrib import admin
from .models import FraudCase


@admin.register(FraudCase)
class FraudCaseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "transaction",
        "status",
        "priority",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
    )

    search_fields = (
        "title",
        "assigned_to",
    )