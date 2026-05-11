from giftcard.models import Cart
from giftcard.services.cart_service import CartService

def cart_count(request):
    count = 0
    # To avoid creating a session for every anonymous hit, we only query if needed
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if cart and cart.items:
                count = sum(item.get("quantity", 1) for item in cart.items)
        except Exception:
            pass
    elif request.session.session_key:
        try:
            cart = Cart.objects.filter(session_key=request.session.session_key, is_active=True).first()
            if cart and cart.items:
                count = sum(item.get("quantity", 1) for item in cart.items)
        except Exception:
            pass
            
    return {
        "global_cart_count": count
    }
