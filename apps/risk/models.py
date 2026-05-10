from django.db import models


class RiskAssessment(models.Model):
    transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.CASCADE,
        related_name="risk_assessment",
    )
    total_score = models.IntegerField()
    risk_level = models.CharField(max_length=50)
    decision = models.CharField(max_length=50)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)