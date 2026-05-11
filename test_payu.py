import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentpeeps.settings")
django.setup()

from giftcard.models import Order
from giftcard.payments.registry import get_gateway
from decimal import Decimal
import uuid

try:
    gw = get_gateway("payu")
    res = gw.create_order(
        amount=Decimal("150.00"),
        currency="INR",
        reference_id=str(uuid.uuid4()),
        customer={"name": "Test User", "email": "test@example.com", "phone": "9999999999"},
        surl="http://localhost:8000/success",
        furl="http://localhost:8000/failure"
    )
    print("SUCCESS", res.gateway_type)
except Exception as e:
    import traceback
    traceback.print_exc()

