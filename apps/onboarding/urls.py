from django.urls import path
from .views import TenantOnboardingView, DeveloperConsoleView

urlpatterns = [
    path("register/", TenantOnboardingView.as_view(), name="tenant-register"),
    path(
        "developer-console/",
        DeveloperConsoleView.as_view(),
        name="developer-console",
    ),
]