from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "customer_msisdn",
        "amount",
        "currency",
        "txn_type",
        "status",
        "risk_score",
        "created_at",
    )
    search_fields = ("customer_msisdn", "device_id", "agent_id")
    list_filter = ("status", "txn_type", "currency")