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
        return

    date_at_client = timezone.now().isoformat()
    refno = f"STDPS-{uuid.uuid4().hex}"
    
    # -------------------------------------------------------------
    # Create Order API Curl (syncOnly=true with SKU CNPIN)
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
                "amount": 1000
            }
        ],
        "products": [
            {
                "sku": "CNPIN",
                "price": 1000,
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

    print("\n" + "="*80)
    print("CURL FOR TEST CASE #5: CREATE ORDER API (syncOnly=true with SKU CNPIN)")
    print("="*80)
    print(order_curl)
    print("="*80 + "\n")

if __name__ == "__main__":
    generate_curls()
