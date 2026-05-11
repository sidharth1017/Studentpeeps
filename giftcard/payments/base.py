"""
Payment Gateway Base
====================
Abstract base class all payment gateway providers must implement.

Gateway Types
-------------
- "modal"    : JS-based modal in browser (e.g. Razorpay). Frontend calls initiate → opens modal → POSTs result back.
- "redirect" : Server-rendered form that is submitted to the gateway URL (e.g. PayU, CCAvenue).
               Frontend calls initiate → receives form fields → auto-submits HTML form to gateway.

To add a new gateway (Stripe, Pine Labs, etc.):
  1. Create giftcard/payments/<provider>.py
  2. Subclass PaymentGateway, set GATEWAY_TYPE = "modal" or "redirect"
  3. Implement create_order() and verify_payment()
  4. Register in GATEWAY_REGISTRY in registry.py (1 line)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class PaymentOrderResult:
    """Returned by create_order() — all data the frontend/view needs."""

    gateway_order_id: str       # unique order/txn id from gateway
    amount_paise: int           # amount in smallest currency unit (paise for INR)
    currency: str               # "INR"
    gateway_key: str            # public merchant key exposed to browser

    # "modal" → Razorpay-style JS SDK
    # "redirect" → form POST to gateway URL (PayU, CCAvenue, etc.)
    gateway_type: str = "modal"

    # For redirect gateways: URL the form POSTs to
    action_url: str = ""

    # For redirect gateways: flat dict of all <input> fields to POST
    form_fields: Dict[str, str] = field(default_factory=dict)

    # Any other gateway-specific extras
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentVerificationResult:
    success: bool
    gateway_payment_id: str     # e.g. razorpay_payment_id or payu mihpayid
    error_message: str = ""


class PaymentGateway(ABC):
    """All payment gateways inherit from this."""

    GATEWAY_TYPE: str = "modal"   # override in subclass

    @abstractmethod
    def create_order(
        self,
        amount: Decimal,
        currency: str,
        reference_id: str,
        customer: Optional[Dict[str, str]] = None,
        surl: str = "",
        furl: str = "",
    ) -> PaymentOrderResult:
        """
        Create a payment order / gather all data needed to initiate payment.

        Args:
            amount:       Total amount in rupees (Decimal)
            currency:     "INR"
            reference_id: Our internal unique order reference (UUID)
            customer:     {"name": str, "email": str, "phone": str}  — required by redirect gateways
            surl:         Success redirect URL  (required by redirect gateways)
            furl:         Failure redirect URL  (required by redirect gateways)

        Returns:
            PaymentOrderResult
        """
        ...

    @abstractmethod
    def verify_payment(self, payload: Dict[str, str]) -> PaymentVerificationResult:
        """
        Verify the payment result (signature/hash) from the gateway callback.

        Args:
            payload: All POST/GET params sent by the gateway callback

        Returns:
            PaymentVerificationResult
        """
        ...
