from django.conf import settings
from django.utils import timezone

from utilities.httpClient.http_client import HttpClient
from giftcard.models import ProviderApiLog
from .token_manager import WoohooTokenManager
from .signature import WoohooSignature


class WoohooApiClient:
    def __init__(self, provider):
        self.provider = provider
        timeout = getattr(settings, 'WOOHOO_TIMEOUT', 40)
        self.http = HttpClient(timeout=timeout)
        self.token_manager = WoohooTokenManager(provider)

    def request(self, method, endpoint, query=None, body=None):
        import json
        from utilities.httpClient.exceptions import HttpTimeout, HttpRequestFailed
        
        url = settings.WOOHOO_BASE_URL + endpoint
        max_retries = 3
        last_exception = None

        for attempt in range(max_retries):
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

            request_kwargs = {"params": query}
            if body:
                # We MUST send the exact string the signature was generated from
                sorted_body = WoohooSignature._sort_json(body)
                body_json_str = json.dumps(sorted_body, separators=(",", ":"))
                request_kwargs["data"] = body_json_str

            response_status = 500
            response_data = None
            duration_ms = 0
            start_time = timezone.now()

            try:
                response = self.http.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **request_kwargs
                )
                response_status = response["status_code"]
                response_data = response["data"]
                duration_ms = response.get("duration_ms", 0)
                
                # Successful request, break the retry loop
                self._log_api_call(method, url, headers, body, response_status, response_data, signature, duration_ms, start_time)
                return response_data

            except HttpRequestFailed as e:
                response_status = e.status_code
                try:
                    response_data = json.loads(e.response)
                except:
                    response_data = e.response
                
                self._log_api_call(method, url, headers, body, response_status, response_data, signature, duration_ms, start_time)

                if response_status == 401:
                    # Token rejected, refresh and retry
                    self.token_manager._refresh()
                    last_exception = e
                    continue
                else:
                    # Other error, stop retrying
                    raise e
            except Exception as e:
                response_data = str(e)
                self._log_api_call(method, url, headers, body, response_status, response_data, signature, duration_ms, start_time)
                raise e

        # If we reached here, it means we exhausted retries with 401
        if last_exception:
            raise last_exception

    def _log_api_call(self, method, url, headers, body, status, response, signature, duration, start_time):
        from giftcard.models import ProviderApiLog
        from django.utils import timezone
        
        if duration == 0:
            duration = int((timezone.now() - start_time).total_seconds() * 1000)

        ProviderApiLog.objects.create(
            provider=self.provider,
            method=method,
            url=url,
            request_headers=headers,
            request_body=body,
            response_status=status,
            response_body=response,
            signature=signature,
            duration_ms=duration
        )
