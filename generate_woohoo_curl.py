import os
import django
import json
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentpeeps.settings")
django.setup()

from django.conf import settings
from django.utils import timezone
from giftcard.models import Provider
from giftcard.providers.woohoo.token_manager import WoohooTokenManager
from giftcard.providers.woohoo.signature import WoohooSignature
from giftcard.providers.woohoo import endpoints

def generate_woohoo_order_curl():
    provider = Provider.objects.get(id="woohoo")
    token_manager = WoohooTokenManager(provider)
    
    # 1. Get fresh token
    token = token_manager.get_token()
    date_at_client = timezone.now().isoformat()
    
    # 2. Define endpoint mapping and valid V3 payload
    url = settings.WOOHOO_BASE_URL + endpoints.ORDER
    method = "POST"
    
    payload = {
        "address": {
            "firstname": "Curl",
            "lastname": "Test",
            "email": "test@example.com",
            "telephone": "+919999999999",
            "country": "IN",
            "billToThis": True
        },
        "billing": {
            "firstname": "Curl",
            "lastname": "Test",
            "email": "test@example.com",
            "telephone": "+919999999999",
            "country": "IN"
        },
        "deliveryMode": "API",
        "payments": [
            {
                "code": "svc",
                "amount": 500  # valid denomination
            }
        ],
        "products": [
            {
                "sku": "EGCGBAMZ001",
                 "price": 500,
                 "qty": 1,
                 "currency": 356
            }
        ],
        "refno": f"test-order-{int(datetime.now().timestamp())}",
        "syncOnly": False
    }
    
    # 3. Generate correct string
    sorted_body = WoohooSignature._sort_json(payload)
    body_json_str = json.dumps(sorted_body, separators=(",", ":"))
    
    # 4. Generate precise HMAC signature
    signature = WoohooSignature.generate(
        method=method,
        url=url,
        query=None,
        body=payload,
        secret=settings.WOOHOO_CLIENT_SECRET
    )
    
    # 5. Build curl string
    curl_command = f"""curl -X POST "{url}" \\
     -H "Authorization: Bearer {token}" \\
     -H "Content-Type: application/json" \\
     -H "dateAtClient: {date_at_client}" \\
     -H "signature: {signature}" \\
     -d '{body_json_str}'"""
     
    print("\n\n" + "="*80)
    print("READY TO USE CURL COMMAND (Valid for a few minutes):")
    print("="*80 + "\n")
    print(curl_command)
    print("\n" + "="*80)

if __name__ == "__main__":
    generate_woohoo_order_curl()
