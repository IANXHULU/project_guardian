import uuid
from django.db import models


class AlertNotification(models.Model):
    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("webhook", "Webhook"),
        ("sms", "SMS"),
        ("slack", "Slack"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.CASCADE,
        related_name="alert_notifications",
    )

    channel = models.CharField(max_length=30, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")

    recipient = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()

    response_payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.channel} | {self.status} | {self.transaction_id}"