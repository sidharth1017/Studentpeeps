"""
Razorpay Payment Gateway
"""
import razorpay
import hmac
import hashlib
from decimal import Decimal
from typing import Dict, Optional
from django.conf import settings

from .base import PaymentGateway, PaymentOrderResult, PaymentVerificationResult


class RazorpayGateway(PaymentGateway):
    """
    Implements Razorpay payment gateway (JS modal flow).
    Docs: https://razorpay.com/docs/payment-gateway/web-integration/standard/
    """

    GATEWAY_TYPE = "modal"

    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    def create_order(
        self,
        amount: Decimal,
        currency: str,
        reference_id: str,
        customer: Optional[Dict[str, str]] = None,
        surl: str = "",
        furl: str = "",
    ) -> PaymentOrderResult:
        """Creates a Razorpay order. Amount in rupees → converted to paise."""
        amount_paise = int(amount * 100)

        rzp_order = self.client.order.create(data={
            "amount":          amount_paise,
            "currency":        currency,
            "receipt":         reference_id,
            "payment_capture": 1,
        })

        return PaymentOrderResult(
            gateway_order_id=rzp_order["id"],
            amount_paise=amount_paise,
            currency=currency,
            gateway_key=settings.RAZORPAY_KEY_ID,
            gateway_type="modal",
        )

    def verify_payment(self, payload: Dict[str, str]) -> PaymentVerificationResult:
        """Verifies Razorpay HMAC-SHA256 signature from payment callback."""
        try:
            razorpay_order_id   = payload.get("razorpay_order_id", "")
            razorpay_payment_id = payload.get("razorpay_payment_id", "")
            razorpay_signature  = payload.get("razorpay_signature", "")

            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
                hashlib.sha256
            ).hexdigest()

            if generated_signature == razorpay_signature:
                return PaymentVerificationResult(success=True, gateway_payment_id=razorpay_payment_id)
            else:
                return PaymentVerificationResult(
                    success=False,
                    gateway_payment_id=razorpay_payment_id,
                    error_message="Signature mismatch — possible tampered response"
                )
        except Exception as e:
            return PaymentVerificationResult(success=False, gateway_payment_id="", error_message=str(e))
