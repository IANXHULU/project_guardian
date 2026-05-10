from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import OnboardingSerializer
from .models import TenantAPIKey
from apps.tenants.models import Tenant
from apps.transactions.models import Transaction
from apps.authentication.api_key_auth import GuardianAPIKeyAuthentication


class TenantOnboardingView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OnboardingSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        onboarding = serializer.save(
            is_verified=True
        )

        tenant = Tenant.objects.create(
            name=onboarding.company_name
        )

        keys = TenantAPIKey.objects.create(
            tenant=tenant
        )

        return Response(
            {
                "success": True,
                "message": "Tenant onboarded successfully.",
                "tenant_id": str(tenant.id),
                "company_name": tenant.name,
                "api_key": keys.api_key,
                "secret_key": keys.secret_key,
            },
            status=status.HTTP_201_CREATED
        )


class DeveloperConsoleView(APIView):
    authentication_classes = [GuardianAPIKeyAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        tenant = request.tenant

        credentials = TenantAPIKey.objects.filter(
            tenant=tenant
        ).first()

        transactions = Transaction.objects.filter(
            tenant=tenant
        )

        total_transactions = transactions.count()
        approved_count = transactions.filter(
            status="approved"
        ).count()

        flagged_count = transactions.filter(
            status="flagged"
        ).count()

        blocked_count = transactions.filter(
            status="blocked"
        ).count()

        masked_secret = None

        if credentials and credentials.secret_key:
            masked_secret = (
                credentials.secret_key[:6]
                + "..."
                + credentials.secret_key[-6:]
            )

        return Response(
            {
                "success": True,
                "tenant": {
                    "id": str(tenant.id),
                    "name": tenant.name,
                },
                "api_credentials": {
                    "api_key": credentials.api_key if credentials else None,
                    "secret_key": masked_secret,
                },
                "usage": {
                    "total_transactions": total_transactions,
                    "approved": approved_count,
                    "flagged": flagged_count,
                    "blocked": blocked_count,
                },
                "integration_status": {
                    "has_api_key": credentials is not None,
                    "has_sent_transaction": total_transactions > 0,
                    "status": (
                        "active"
                        if total_transactions > 0
                        else "pending_first_transaction"
                    ),
                },
                "sample_request": {
                    "url": "/api/v1/transactions/",
                    "method": "POST",
                    "headers": {
                        "X-Guardian-API-Key": "YOUR_API_KEY",
                        "X-Guardian-Secret": "YOUR_SECRET_KEY",
                    },
                },
            }
        )