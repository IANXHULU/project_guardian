class TransactionDecision(models.Model):
    transaction_id = models.CharField(max_length=100)
    decision = models.CharField(max_length=20)
    risk_score = models.IntegerField()
    reason = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)