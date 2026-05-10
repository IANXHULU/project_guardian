import uuid
from django.db import models


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("flagged", "Flagged"),
        ("delayed", "Delayed"),
        ("blocked", "Blocked"),
    ]

    TXN_TYPES = [
        ("cash_in", "Cash In"),
        ("cash_out", "Cash Out"),
        ("transfer", "Transfer"),
        ("payment", "Payment"),
        ("withdrawal", "Withdrawal"),
        ("float_transfer", "Float Transfer"),
        ("adjustment", "Adjustment"),
        ("reversal", "Reversal"),
        ("pin_reset", "PIN Reset"),
        ("profile_change", "Profile Change"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    customer_msisdn = models.CharField(max_length=20)

    source_account = models.CharField(max_length=100, blank=True, null=True)
    destination_account = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=150, blank=True, null=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10, default="ZMW")
    txn_type = models.CharField(max_length=50, choices=TXN_TYPES)

    device_id = models.CharField(max_length=255, blank=True, null=True)
    agent_id = models.CharField(max_length=255, blank=True, null=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    risk_score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.txn_type} | {self.customer_msisdn} | {self.amount} {self.currency}"
    
    
class TransactionReviewLog(models.Model):
    ACTION_CHOICES = [
        ("approved", "Approved"),
        ("blocked", "Blocked"),
        ("escalated", "Escalated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="review_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    reviewer = models.CharField(max_length=150, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)