from django.urls import path
from .views import (
    DashboardSummaryView,
    GuardianDashboardView,
    onboard_page,
    fraud_portal_page,
)

urlpatterns = [
    # Existing analytics API
    path(
        "summary/",
        DashboardSummaryView.as_view(),
        name="dashboard-summary"
    ),

    # Existing fraud analytics HTML dashboard
    path(
        "guardian/",
        GuardianDashboardView.as_view(),
        name="guardian-dashboard"
    ),

    # New onboarding UI
    path(
        "onboard/",
        onboard_page,
        name="onboard-page"
    ),

    # New tenant fraud portal UI
    path(
        "fraud/",
        fraud_portal_page,
        name="fraud-portal-page"
    ),
]