from django.contrib import admin
from .models import RiskAssessment


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("transaction", "total_score", "risk_level", "decision", "created_at")
    list_filter = ("risk_level", "decision")