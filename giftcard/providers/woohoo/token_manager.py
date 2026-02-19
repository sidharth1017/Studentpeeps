from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from utilities.httpClient.http_client import HttpClient
from giftcard.models import ProviderAuthToken
from . import endpoints


class WoohooTokenManager:
    def __init__(self, provider):
        self.provider = provider
        self.http = HttpClient()

    def get_token(self):
        token = ProviderAuthToken.objects.filter(
            provider=self.provider,
            is_active=True
        ).first()

        if token and token.expires_at > timezone.now():
            return token.access_token

        return self._refresh()

    def _refresh(self):
        """
        Fetch new Woohoo token and store it with a 14-day expiry.
        """

        auth_code = self._get_authorization_code()
        token_data = self._get_access_token(auth_code)

        access_token = token_data["token"]
        expires_at = timezone.now() + timedelta(days=14)

        ProviderAuthToken.objects.filter(
            provider=self.provider,
            is_active=True
        ).update(is_active=False)

        ProviderAuthToken.objects.create(
            provider=self.provider,
            access_token=access_token,
            expires_at=expires_at,
            is_active=True
        )

        return access_token


    def _get_authorization_code(self):
        resp = self.http.request(
            "POST",
            settings.WOOHOO_BASE_URL + endpoints.VERIFY,
            json={
                "clientId": settings.WOOHOO_CLIENT_ID,
                "username": settings.WOOHOO_USERNAME,
                "password": settings.WOOHOO_PASSWORD,
            }
        )
        return resp["data"]["authorizationCode"]

    def _get_access_token(self, auth_code):
        resp = self.http.request(
            "POST",
            settings.WOOHOO_BASE_URL + endpoints.TOKEN,
            json={
                "clientId": settings.WOOHOO_CLIENT_ID,
                "clientSecret": settings.WOOHOO_CLIENT_SECRET,
                "authorizationCode": auth_code,
            }
        )
        return resp["data"]
