from django.urls import path
from .views import (
    TransactionCreateView,
    ReviewQueueView,
    ApproveTransactionView,
    BlockTransactionView,
    EscalateTransactionView
)

urlpatterns = [
    path(
        "transactions/",
        TransactionCreateView.as_view(),
        name="transaction-create"
    ),

    path(
        "review-queue/",
        ReviewQueueView.as_view(),
        name="review-queue"
    ),

    path(
        "review-queue/<uuid:transaction_id>/approve/",
        ApproveTransactionView.as_view(),
        name="approve-transaction"
    ),

    path(
        "review-queue/<uuid:transaction_id>/block/",
        BlockTransactionView.as_view(),
        name="block-transaction"
    ),

    path(
        "review-queue/<uuid:transaction_id>/escalate/",
        EscalateTransactionView.as_view(),
        name="escalate-transaction"
    ),
]