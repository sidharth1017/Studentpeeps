import hmac
import hashlib
import json
import urllib.parse

class WoohooSignature:
    @staticmethod
    def _encode(value: str) -> str:
        return urllib.parse.quote(value, safe="~")

    @classmethod
    def generate(cls, method, url, query=None, body=None, secret=""):
        method = method.upper()

        if query:
            query_string = "&".join(f"{k}={query[k]}" for k in sorted(query))
            url = f"{url}?{query_string}"

        encoded_url = cls._encode(url)
        base = f"{method}&{encoded_url}"

        if body:
            sorted_body = cls._sort_json(body)
            body_json = json.dumps(sorted_body, separators=(",", ":"))
            encoded_body = cls._encode(body_json)
            base = f"{base}&{encoded_body}"

        return hmac.new(
            secret.encode(),
            base.encode(),
            hashlib.sha512
        ).hexdigest()

    @staticmethod
    def _sort_json(data):
        if isinstance(data, dict):
            return {k: WoohooSignature._sort_json(data[k]) for k in sorted(data)}
        if isinstance(data, list):
            return [WoohooSignature._sort_json(i) for i in data]
        return data
