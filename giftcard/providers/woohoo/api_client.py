from django.conf import settings
from django.utils import timezone

from utilities.httpClient.http_client import HttpClient
from giftcard.models import ProviderApiLog
from .token_manager import WoohooTokenManager
from .signature import WoohooSignature


class WoohooApiClient:
    def __init__(self, provider):
        self.provider = provider
        self.http = HttpClient()
        self.token_manager = WoohooTokenManager(provider)

    def request(self, method, endpoint, query=None, body=None):
        url = settings.WOOHOO_BASE_URL + endpoint

        token = self.token_manager.get_token()
        date_at_client = timezone.now().isoformat()

        signature = WoohooSignature.generate(
            method=method,
            url=url,
            query=query,
            body=body,
            secret=settings.WOOHOO_CLIENT_SECRET
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "dateAtClient": date_at_client,
            "signature": signature
        }

        response = self.http.request(
            method=method,
            url=url,
            headers=headers,
            params=query,
            json=body
        )

        ProviderApiLog.objects.create(
            provider=self.provider,
            method=method,
            url=url,
            request_headers=headers,
            request_body=body,
            response_status=response["status_code"],
            response_body=response["data"],
            signature=signature,
            duration_ms=response["duration_ms"]
        )

        return response["data"]
