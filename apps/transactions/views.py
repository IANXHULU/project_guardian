from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Transaction
from .serializers import TransactionCreateSerializer
from apps.telecom.services import run_telecom_checks
from apps.risk.engine import assess_transaction
from apps.cases.models import FraudCase
from apps.authentication.api_key_auth import (
    GuardianAPIKeyAuthentication
)

class TransactionCreateView(APIView):
    authentication_classes = [GuardianAPIKeyAuthentication]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TransactionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction = serializer.save(
            tenant=request.tenant
        )

        telecom_data = run_telecom_checks(transaction)
        risk_result = assess_transaction(transaction, telecom_data)

        return Response(
            {
                "success": True,
                "transaction_id": str(transaction.id),
                "status": risk_result["status"],
                "risk_score": risk_result["score"],
                "risk_level": risk_result["risk_level"],
                "decision": risk_result["decision"],
                "explanation": risk_result["explanation"],
                "references": risk_result["references"],
                "telecom_checks": telecom_data,
                "tenant": request.tenant.name,
            },
            status=status.HTTP_201_CREATED,
        )

class ReviewQueueView(APIView):
    authentication_classes = [
        GuardianAPIKeyAuthentication
    ]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        flagged_transactions = Transaction.objects.filter(
            status="flagged"
        ).order_by("-created_at")

        data = []

        for txn in flagged_transactions:
            data.append(
                {
                    "transaction_id": str(txn.id),
                    "customer_msisdn": txn.customer_msisdn,
                    "source_account": txn.source_account,
                    "destination_account": txn.destination_account,
                    "amount": str(txn.amount),
                    "currency": txn.currency,
                    "txn_type": txn.txn_type,
                    "risk_score": txn.risk_score,
                    "status": txn.status,
                    "created_at": txn.created_at,
                }
            )

        return Response(
            {
                "count": len(data),
                "results": data,
            }
        )


class ApproveTransactionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id)

        if transaction.status != "flagged":
            return Response(
                {"error": "Only flagged transactions can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction.status = "approved"
        transaction.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "message": "Transaction approved successfully.",
                "transaction_id": str(transaction.id),
                "status": transaction.status,
            }
        )


class BlockTransactionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id)

        if transaction.status != "flagged":
            return Response(
                {"error": "Only flagged transactions can be blocked."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction.status = "blocked"
        transaction.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "message": "Transaction blocked successfully.",
                "transaction_id": str(transaction.id),
                "status": transaction.status,
            }
        )


class EscalateTransactionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id)

        case = FraudCase.objects.create(
            transaction=transaction,
            title=f"Fraud Review - {transaction.customer_msisdn}",
            status="open",
        )

        return Response(
            {
                "success": True,
                "message": "Transaction escalated successfully.",
                "case_id": str(case.id),
                "transaction_id": str(transaction.id),
            },
            status=status.HTTP_201_CREATED,
        )