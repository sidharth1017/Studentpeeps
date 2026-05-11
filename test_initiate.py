import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentpeeps.settings")
django.setup()

from django.test import Client
from giftcard.models import Cart
from django.contrib.auth.models import User

try:
    c = Client()
    # Create test user and cart
    u, _ = User.objects.get_or_create(username="test", email="test@test.com")
    u.set_password("pass")
    u.save()
    
    cart, _ = Cart.objects.get_or_create(user=u)
    cart.items = [{"sku": "test", "denomination": "100", "quantity": 1, "final_price": "100"}]
    cart.save()
    
    c.force_login(u)
    
    response = c.post('/giftcard/payment/initiate/', {
        "name": "Test User",
        "email": "test@test.com",
        "phone": "9999999999"
    }, content_type="application/json")
    
    print("STATUS_CODE:", response.status_code)
    try:
        print("JSON:", response.json())
    except:
        print("CONTENT:", response.content.decode())
except Exception as e:
    import traceback
    traceback.print_exc()
