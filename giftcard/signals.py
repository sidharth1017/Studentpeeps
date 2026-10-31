from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from giftcard.services.cart_service import CartService

@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    """
    When a user logs in, merge their guest cart into their user cart.
    """
    service = CartService(request)
    guest_key = getattr(request, "_guest_cart_session_key", None)
    service.merge_guest_cart(user, guest_session_key=guest_key)
