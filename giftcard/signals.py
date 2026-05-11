from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from giftcard.services.cart_service import CartService

@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    """
    When a user logs in, merge their guest cart into their user cart.
    """
    service = CartService(request)
    service.merge_guest_cart(user)
