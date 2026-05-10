import uuid
from django.db import models


class Tenant(models.Model):
    TENANT_TYPES = [
        ("fintech", "Fintech"),
        ("mno", "Mobile Network Operator"),
        ("bank", "Bank"),
        ("merchant", "Merchant"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)

    tenant_type = models.CharField(
        max_length=50,
        choices=TENANT_TYPES,
        default="fintech",
    )

    email = models.EmailField(blank=True, null=True)

    phone = models.CharField(max_length=50, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name