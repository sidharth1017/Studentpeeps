import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentpeeps.settings")
django.setup()

from giftcard.providers.woohoo.api_client import WoohooApiClient
from giftcard.providers.woohoo import endpoints
from giftcard.models import Provider
import uuid

provider = Provider.objects.get(id="woohoo")
client = WoohooApiClient(provider)

payload = {
  "address": {
    "billToThis": True,
    "email": "hi@studentpeeps.club",
    "firstname": "Sidharth",
    "lastname": "Verma",
    "telephone": "+919876543210",
    "country": "IN"
  },
  "billing": {
    "email": "hi@studentpeeps.club",
    "firstname": "Sidharth",
    "lastname": "Verma",
    "telephone": "+919876543210",
    "country": "IN"
  },
  "deliveryMode": "API",
  "payments": [
    {
      "amount": 100,
      "code": "svc"
    }
  ],
  "products": [
    {
      "currency": 356,
      "price": 100,
      "qty": 1,
      "sku": "EGCGBAMZ001"
    }
  ],
  "refno": f"STDPS-{uuid.uuid4().hex[:8]}",
  "syncOnly": False
}

try:
    res = client.request("POST", endpoints.ORDER, body=payload)
    print("SUCCESS!", res)
except Exception as e:
    print("FAILED!", e)
