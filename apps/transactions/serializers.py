from rest_framework import serializers
from .models import Transaction


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "customer_msisdn",
            "source_account",
            "destination_account",
            "reference",
            "amount",
            "currency",
            "txn_type",
            "device_id",
            "agent_id",
            "latitude",
            "longitude",
            "status",
            "risk_score",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "risk_score",
            "created_at",
        ]