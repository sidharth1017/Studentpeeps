"""
Woohoo Order Service
====================
Handles creating orders on the Woohoo API after payment is confirmed.
Reference: https://developers.woohoo.in/docs/rest-api-v3-revamp/order-api/
"""
import uuid
from django.conf import settings

from giftcard.models import Provider
from giftcard.providers.woohoo.api_client import WoohooApiClient
from giftcard.providers.woohoo import endpoints


class WoohooOrderService:
    """
    Places an order on Woohoo after successful payment.
    The cart items snapshot drives the line items.
    """

    def __init__(self):
        self.provider = Provider.objects.get(id="woohoo")
        self.client = WoohooApiClient(self.provider)

    def create_order(self, our_order, customer: dict) -> dict:
        """
        Args:
            our_order:  giftcard.models.Order instance (already saved, payment confirmed)
            customer:   {"name": str, "email": str, "phone": str}

        Returns:
            Woohoo API response dict
        """
        line_items = self._build_line_items(our_order.items_snapshot)

        # Format fields
        email = customer.get("email", "hi@studentpeeps.club")
        phone = customer.get("phone", "+919876543210")
        if not phone.startswith("+91"):
            phone = f"+91{phone[-10:]}" if len(phone) >= 10 else "+919876543210"

        first_name = (customer.get("name") or "User").split(" ")[0]
        last_name  = " ".join((customer.get("name") or "User").split(" ")[1:]) or "User"

        payload = {
            "address": {
                "firstname": first_name,
                "lastname": last_name,
                "email": email,
                "telephone": phone,
                "country": "IN",
                "billToThis": True
            },
            "billing": {
                "firstname": first_name,
                "lastname": last_name,
                "email": email,
                "telephone": phone,
                "country": "IN"
            },
            "deliveryMode": "API",
            "payments": [
                {
                    "code": "svc",
                    "amount": sum(item["price"] * item["qty"] for item in line_items)
                }
            ],
            "products": line_items,
            "refno": our_order.reference_id,
            "syncOnly": False,
        }

        response = self.client.request(
            method="POST",
            endpoint=endpoints.ORDER,
            body=payload
        )

        return response

    def _build_line_items(self, items_snapshot: list) -> list:
        """
        Converts our cart items snapshot into Woohoo order line items.
        """
        products = []
        for item in items_snapshot:
            products.append({
                "sku": item["sku"],
                "price": int(float(item["denomination"])),
                "qty": int(item["quantity"]),
                "currency": 356
            })
        return products

    def get_order_status(self, woohoo_order_id: str) -> dict:
        """
        Fetches the current status of an order using Woohoo Order ID.
        Endpoint: /rest/v3/orders/{order_id}
        """
        endpoint = endpoints.ORDER_STATUS.format(order_id=woohoo_order_id)
        response = self.client.request(
            method="GET",
            endpoint=endpoint
        )
        return response

    def get_order_status_by_refno(self, refno: str) -> dict:
        """
        Fetches the current status of an order using our reference number (for timeouts).
        Endpoint: /rest/v3/orders/{refno}/status
        """
        endpoint = endpoints.ORDER_STATUS_BY_REFNO.format(refno=refno)
        response = self.client.request(
            method="GET",
            endpoint=endpoint
        )
        return response

    def get_activated_cards(self, order_id_or_refno: str) -> dict:
        """
        Fetches the card details (vouchers) for a specific order.
        Reference: https://developers.woohoo.in/docs/rest-api-v3-revamp/activated-cards-api/
        """
        endpoint = endpoints.ORDER_CARDS.format(order_id=order_id_or_refno)
        response = self.client.request(
            method="GET",
            endpoint=endpoint
        )
        return response
