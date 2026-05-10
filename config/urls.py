from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.transactions.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.urls")),
    path("api/v1/ai/", include("apps.ai_assistant.urls")),
    path("api/v1/onboarding/", include("apps.onboarding.urls")),
]