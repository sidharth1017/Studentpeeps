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

    def _log_auth_call(self, method, url, body, status, response, duration, start_time):
        from giftcard.models import ProviderApiLog
        from django.utils import timezone
        
        if duration == 0:
            duration = int((timezone.now() - start_time).total_seconds() * 1000)

        ProviderApiLog.objects.create(
            provider=self.provider,
            method=method,
            url=url,
            request_headers={"Content-Type": "application/json"},
            request_body=body,
            response_status=status,
            response_body=response,
            signature="",
            duration_ms=duration
        )

    def _make_auth_request(self, endpoint, payload):
        import json
        from django.utils import timezone
        from utilities.httpClient.exceptions import HttpTimeout, HttpRequestFailed
        
        url = settings.WOOHOO_BASE_URL + endpoint
        start_time = timezone.now()
        response_status = 500
        response_data = None
        duration_ms = 0
        
        try:
            resp = self.http.request(
                "POST",
                url,
                json=payload
            )
            response_status = resp["status_code"]
            response_data = resp["data"]
            duration_ms = resp.get("duration_ms", 0)
            
            self._log_auth_call("POST", url, payload, response_status, response_data, duration_ms, start_time)
            return response_data
            
        except HttpRequestFailed as e:
            response_status = e.status_code
            try:
                response_data = json.loads(e.response)
            except:
                response_data = e.response
                
            self._log_auth_call("POST", url, payload, response_status, response_data, duration_ms, start_time)
            raise e
        except Exception as e:
            response_data = str(e)
            self._log_auth_call("POST", url, payload, response_status, response_data, duration_ms, start_time)
            raise e

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

        # 1. Delete old inactive token to prevent UNIQUE constraint failure (provider, is_active)
        ProviderAuthToken.objects.filter(
            provider=self.provider,
            is_active=False
        ).delete()
        
        # 2. Deactivate currently active token
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
        payload = {
            "clientId": settings.WOOHOO_CLIENT_ID,
            "username": settings.WOOHOO_USERNAME,
            "password": settings.WOOHOO_PASSWORD,
        }
        data = self._make_auth_request(endpoints.VERIFY, payload)
        return data["authorizationCode"]

    def _get_access_token(self, auth_code):
        payload = {
            "clientId": settings.WOOHOO_CLIENT_ID,
            "clientSecret": settings.WOOHOO_CLIENT_SECRET,
            "authorizationCode": auth_code,
        }
        data = self._make_auth_request(endpoints.TOKEN, payload)
        return data
