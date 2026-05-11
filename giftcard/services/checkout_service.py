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

        order = Order.objects.create(
            user=self.cart.user,
            reference_id=str(uuid4()),
            total_amount=self.cart.total_amount(),
            provider_id="woohoo",
        )

        # Store a static snapshot of items
        order.items_snapshot = self.cart.items
        order.save()

        # Final order placed, retire the cart
        self.cart.is_active = False
        self.cart.save()
        
        # Alternatively, if we just delete it:
        self.cart.delete()

        return order
