import uuid
import secrets
from django.db import models


class OnboardingRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255)
    admin_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class TenantAPIKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE
    )
    api_key = models.CharField(max_length=255, unique=True)
    secret_key = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = f"gdn_live_{secrets.token_hex(16)}"

        if not self.secret_key:
            self.secret_key = secrets.token_hex(32)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"API Key for {self.tenant.name}"