import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentpeeps.settings")
django.setup()

from django.test import RequestFactory
from giftcard.views import InitiatePaymentView
from giftcard.models import Cart
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
import json

try:
    factory = RequestFactory()
    request = factory.post('/giftcard/payment/initiate/', data=json.dumps({
        "name": "Test User",
        "email": "test@test.com",
        "phone": "9999999999"
    }), content_type="application/json")
    
    # Set up session
    request.session = SessionStore()
    request.session.save()
    
    u, _ = User.objects.get_or_create(username="test", email="test@test.com")
    request.user = u
    
    # Set up cart in session cache format because CartService relies on request.user
    cart, _ = Cart.objects.get_or_create(user=u, is_active=True)
    cart.items = [{"sku": "test", "denomination": "100", "quantity": 1, "final_price": "100"}]
    cart.save()

    view = InitiatePaymentView.as_view()
    response = view(request)
    
    print("STATUS_CODE:", response.status_code)
    try:
        if hasattr(response, 'rendered_content'):
            print("CONTENT:", response.rendered_content)
        elif hasattr(response, 'content'):
            print("CONTENT B:", response.content)
            data = json.loads(response.content.decode('utf-8'))
            print("PARAMS:", data.keys())
            if 'form_fields' in data:
                print("HASH:", data['form_fields']['hash'])
        else:
             print("RESPONSE CLASS:", type(response))
    except Exception as e:
        print("COULD NOT PARSE RESPONSE:", e)
        print("CONTENT:", response.content)
except Exception as e:
    import traceback
    traceback.print_exc()
