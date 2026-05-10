from django.urls import path
from .views import TransactionProcessView

urlpatterns = [
    path(
        "transactions/process/",
        TransactionProcessView.as_view(),
        name="process-transaction",
    ),
]
