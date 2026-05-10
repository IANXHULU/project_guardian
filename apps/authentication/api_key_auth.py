from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.onboarding.models import TenantAPIKey


class GuardianAPIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("X-Guardian-API-Key")
        secret_key = request.headers.get("X-Guardian-Secret")

        if not api_key or not secret_key:
            raise AuthenticationFailed(
                "API credentials were not provided."
            )

        try:
            credentials = TenantAPIKey.objects.select_related(
                "tenant"
            ).get(
                api_key=api_key,
                secret_key=secret_key
            )
        except TenantAPIKey.DoesNotExist:
            raise AuthenticationFailed(
                "Invalid API credentials."
            )

        request.tenant = credentials.tenant

        return (None, None)