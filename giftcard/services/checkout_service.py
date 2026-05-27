from django.db import transaction
from giftcard.models import Order
from uuid import uuid4


class CheckoutService:

    def __init__(self, cart):
        self.cart = cart

    @transaction.atomic
    def create_order(self):
        """
        Creates Order and clears Cart
        """
        if not self.cart.items:
            raise ValueError("Cannot create order from empty cart")

        from django.conf import settings
        org_code = getattr(settings, "WOOHOO_ORG_CODE", "STDPS")

        order = Order.objects.create(
            user=self.cart.user,
            reference_id=f"{org_code}-{uuid4().hex}",
            total_amount=self.cart.total_amount(),
            provider_id="woohoo",
        )

        # Store a static snapshot of items
        order.items_snapshot = self.cart.items
        order.save()

        # Final order placed, delete the cart
        self.cart.delete()

        return order
