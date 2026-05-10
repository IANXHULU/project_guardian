from django.urls import path
from .views import AIInvestigatorView

urlpatterns = [
    path("investigate/<uuid:transaction_id>/", AIInvestigatorView.as_view(), name="ai-investigate"),
]