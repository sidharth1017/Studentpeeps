import os
import django
import json
import uuid
import sys
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentpeeps.settings")
django.setup()

from django.conf import settings
from django.utils import timezone
from giftcard.models import Provider
from giftcard.providers.woohoo.token_manager import WoohooTokenManager
from giftcard.providers.woohoo.signature import WoohooSignature
from giftcard.providers.woohoo import endpoints

def generate_curls():
    try:
        provider = Provider.objects.get(id="woohoo")
    except Provider.DoesNotExist:
        print("Error: Provider 'woohoo' not found in database.")
        return

    token_manager = WoohooTokenManager(provider)
    
    print("Fetching fresh OAuth token from Woohoo...")
    try:
        token = token_manager.get_token()
    except Exception as e:
        print(f"Error fetching token: {e}")
        print("Make sure this script is run from a server whose IP is whitelisted in Woohoo UAT.")
        return

    date_at_client = timezone.now().isoformat()
    refno = f"STDPS-{uuid.uuid4().hex}"
    
    # -------------------------------------------------------------
    # 1. Create Order API Curl
    # -------------------------------------------------------------
    order_url = settings.WOOHOO_BASE_URL + endpoints.ORDER
    order_payload = {
        "address": {
            "firstname": "Test",
            "lastname": "User",
            "email": "hi@studentpeeps.club",
            "telephone": "+919876543210",
            "country": "IN",
            "billToThis": True
        },
        "billing": {
            "firstname": "Test",
            "lastname": "User",
            "email": "hi@studentpeeps.club",
            "telephone": "+919876543210",
            "country": "IN"
        },
        "deliveryMode": "API",
        "payments": [
            {
                "code": "svc",
                "amount": 100
            }
        ],
        "products": [
            {
                "sku": "testsuccess001",
                "price": 100,
                "qty": 1,
                "currency": 356
            }
        ],
        "refno": refno,
        "syncOnly": True
    }
    
    sorted_body = WoohooSignature._sort_json(order_payload)
    body_json_str = json.dumps(sorted_body, separators=(",", ":"))
    
    order_signature = WoohooSignature.generate(
        method="POST",
        url=order_url,
        query=None,
        body=order_payload,
        secret=settings.WOOHOO_CLIENT_SECRET
    )
    
    order_curl = f"""curl -X POST "{order_url}" \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json" \\
  -H "dateAtClient: {date_at_client}" \\
  -H "signature: {order_signature}" \\
  -d '{body_json_str}'"""

    # -------------------------------------------------------------
    # 2. Check Order Status Curl (by Reference Number)
    # -------------------------------------------------------------
    status_url = f"{settings.WOOHOO_BASE_URL}/rest/v3/orders/{refno}/status"
    status_signature = WoohooSignature.generate(
        method="GET",
        url=status_url,
        query=None,
        body=None,
        secret=settings.WOOHOO_CLIENT_SECRET
    )
    
    status_curl = f"""curl -X GET "{status_url}" \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json" \\
  -H "dateAtClient: {date_at_client}" \\
  -H "signature: {status_signature}" """

    # -------------------------------------------------------------
    # Output Generated Curls
    # -------------------------------------------------------------
    print("\n" + "="*80)
    print("CURL 1: CREATE ORDER API (syncOnly=true with SKU testsuccess001)")
    print("="*80)
    print(order_curl)
    
    print("\n" + "="*80)
    print("CURL 2: CHECK ORDER STATUS API (Using reference number, run after 40 seconds)")
    print("="*80)
    print(status_curl)
    
    print("\n" + "="*80)
    print("CURL 3: GENERATE ACTIVATED CARDS API CURL")
    print("="*80)
    print("Since the Activated Cards API requires the 'orderId' returned in response to the status API,")
    print("you can run the following quick python helper to generate its curl once you get the orderId:\n")
    print(f"python3 -c \"")
    print(f"import os, django, sys; sys.path.append('{os.path.dirname(os.path.abspath(__file__))}'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentpeeps.settings'); django.setup()")
    print(f"from django.conf import settings; from django.utils import timezone; from giftcard.models import Provider")
    print(f"from giftcard.providers.woohoo.token_manager import WoohooTokenManager; from giftcard.providers.woohoo.signature import WoohooSignature")
    print(f"order_id = input('Enter the orderId from status response: ').strip()")
    print(f"token = WoohooTokenManager(Provider.objects.get(id='woohoo')).get_token()")
    print(f"date = timezone.now().isoformat()")
    print(f"url = f'{{settings.WOOHOO_BASE_URL}}/rest/v3/order/{{order_id}}/cards/'")
    print(f"sig = WoohooSignature.generate('GET', url, None, None, settings.WOOHOO_CLIENT_SECRET)")
    print(f"print(f\\\"\\\\ncurl -X GET \\\\\\\"{{url}}\\\\\\\" -H \\\\\\\"Authorization: Bearer {{token}}\\\\\\\" -H \\\\\\\"Content-Type: application/json\\\\\\\" -H \\\\\\\"dateAtClient: {{date}}\\\\\\\" -H \\\\\\\"signature: {{sig}}\\\\\\\"\\\")")
    print(f"\"")
    print("="*80 + "\n")

if __name__ == "__main__":
    generate_curls()
