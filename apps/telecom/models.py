from django.db import models


class TelecomCheck(models.Model):
    CHECK_TYPES = [
        ("number_verification", "Number Verification"),
        ("sim_swap", "SIM Swap"),
        ("device_swap", "Device Swap"),
        ("location_verification", "Location Verification"),
        ("kyc_match", "KYC Match"),
("kyc_tenure", "KYC Tenure"),
    ]

    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.CASCADE,
        related_name="telecom_checks",
    )

    

    check_type = models.CharField(max_length=50, choices=CHECK_TYPES)
    provider = models.CharField(max_length=100, default="CAMARA_MOCK")
    result = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    reference = models.CharField(max_length=150, blank=True, null=True)
    response_payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.check_type} | {self.result}"