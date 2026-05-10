from django.contrib import admin
from .models import FraudAlert


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = (
        "rule_code",
        "rule_name",
        "severity",
        "score",
        "reference",
        "transaction",
        "created_at",
    )
    search_fields = ("rule_code", "rule_name", "reference")
    list_filter = ("severity", "rule_code")