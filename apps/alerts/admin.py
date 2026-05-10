from django.contrib import admin
from .models import AlertNotification


@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "channel",
        "status",
        "recipient",
        "subject",
        "transaction",
        "created_at",
        "sent_at",
    )

    list_filter = (
        "channel",
        "status",
    )

    search_fields = (
        "recipient",
        "subject",
        "message",
    )