from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from apps.transactions.serializers import TransactionCreateSerializer
from apps.fraud_detection.services.transaction_processor import process_transaction


class TransactionProcessView(APIView):
    """
    Optional compatibility endpoint.

    Preferred primary endpoint remains apps.transactions.urls:
    POST /api/v1/transactions/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TransactionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transaction = serializer.save()
        result = process_transaction(transaction)

        return Response(
            {
                "success": True,
                **result,
            },
            status=status.HTTP_201_CREATED,
        )
