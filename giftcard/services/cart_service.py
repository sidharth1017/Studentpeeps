from giftcard.models import Cart
from decimal import Decimal


class CartService:

    def __init__(self, request):
        self.request = request
        user_attr = getattr(request, "user", None)
        self.user = user_attr if user_attr and user_attr.is_authenticated else None
        
        # Ensure session exists
        session = getattr(request, "session", None)
        if session:
            if not session.session_key:
                session.create()
            self.session_key = session.session_key
        else:
            self.session_key = None

    # ----------------------------------------
    # Get or Create Cart
    # ----------------------------------------

    def get_cart(self):
        if self.user:
            cart, _ = Cart.objects.get_or_create(
                user=self.user,
                is_active=True
            )
            return cart

        cart, _ = Cart.objects.get_or_create(
            session_key=self.session_key,
            is_active=True
        )
        return cart

    # ----------------------------------------
    # Add Product
    # ----------------------------------------

    def add_item(self, product_data):
        """
        product_data should have: sku, name, denomination, quantity, unit_price, margin, final_price
        """
        cart = self.get_cart()

        items = cart.items

        # Look for existing item with same SKU and denomination
        for item in items:
            if item["sku"] == product_data["sku"] and \
               str(item["denomination"]) == str(product_data["denomination"]):
                item["quantity"] += int(product_data["quantity"])
                cart.save()
                return cart

        items.append(product_data)
        cart.items = items
        cart.save()
        return cart

    # ----------------------------------------
    # Merge Guest Cart on Login
    # ----------------------------------------

    def merge_guest_cart(self, user):
        guest_cart = Cart.objects.filter(
            session_key=self.session_key,
            is_active=True
        ).first()

        if not guest_cart:
            return

        user_cart, _ = Cart.objects.get_or_create(
            user=user,
            is_active=True
        )

        for guest_item in guest_cart.items:
            found = False
            for user_item in user_cart.items:
                if user_item["sku"] == guest_item["sku"] and \
                   str(user_item["denomination"]) == str(guest_item["denomination"]):
                    user_item["quantity"] += guest_item["quantity"]
                    found = True
                    break

            if not found:
                user_cart.items.append(guest_item)

        user_cart.save()
        guest_cart.delete()

    # ----------------------------------------
    # Remove/Update Item (Additional Helpers)
    # ----------------------------------------
    def remove_item(self, sku, denomination):
        cart = self.get_cart()
        items = [item for item in cart.items if not (item["sku"] == sku and str(item["denomination"]) == str(denomination))]
        cart.items = items
        cart.save()
        return cart

    def clear_cart(self):
        cart = self.get_cart()
        cart.items = []
        cart.save()
        return cart
