"""
PayU Payment Gateway (India)
=============================
Redirect-based flow: our backend generates a signed form,
the frontend auto-submits it to PayU's URL. PayU redirects
the user's browser back to our surl/furl after payment.

Hash format (request):
  SHA512( key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5||||||salt )

Hash format (response verification):
  SHA512( salt|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key )

Docs: https://devguide.payu.in/payment-gateway/web-integration/seamless/
"""
import hashlib
from decimal import Decimal
from typing import Dict, Optional
from django.conf import settings

from .base import PaymentGateway, PaymentOrderResult, PaymentVerificationResult


class PayUGateway(PaymentGateway):
    """
    PayU India redirect-based gateway.
    """

    GATEWAY_TYPE = "redirect"

    PAYU_TEST_URL = "https://test.payu.in/_payment"
    PAYU_PROD_URL = "https://secure.payu.in/_payment"

    def __init__(self):
        self.key  = settings.PAYU_MERCHANT_KEY
        self.salt = settings.PAYU_MERCHANT_SALT
        self.use_test = getattr(settings, "PAYU_USE_TEST", True)

    @property
    def action_url(self) -> str:
        return self.PAYU_TEST_URL if self.use_test else self.PAYU_PROD_URL

    # ──────────────────────────────────────────────
    # Hash helpers
    # ──────────────────────────────────────────────

    def _request_hash(
        self,
        txnid: str,
        amount: str,
        productinfo: str,
        firstname: str,
        email: str,
        udf1: str = "",
        udf2: str = "",
        udf3: str = "",
        udf4: str = "",
        udf5: str = "",
    ) -> str:
        """
        Compute SHA512 hash for the payment request.
        Format: key|txnid|amount|productinfo|firstname|email|udf1...udf5||||||salt
        """
        hash_str = (
            f"{self.key}|{txnid}|{amount}|{productinfo}|{firstname}|{email}"
            f"|{udf1}|{udf2}|{udf3}|{udf4}|{udf5}||||||{self.salt}"
        )
        return hashlib.sha512(hash_str.encode("utf-8")).hexdigest()

    def _response_hash(
        self,
        status: str,
        txnid: str,
        amount: str,
        productinfo: str,
        firstname: str,
        email: str,
        udf1: str = "",
        udf2: str = "",
        udf3: str = "",
        udf4: str = "",
        udf5: str = "",
    ) -> str:
        """
        Compute SHA512 hash for response verification (reverse order).
        Format: salt|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key
        """
        hash_str = (
            f"{self.salt}|{status}||||||{udf5}|{udf4}|{udf3}|{udf2}|{udf1}"
            f"|{email}|{firstname}|{productinfo}|{amount}|{txnid}|{self.key}"
        )
        return hashlib.sha512(hash_str.encode("utf-8")).hexdigest()

    # ──────────────────────────────────────────────
    # PaymentGateway interface
    # ──────────────────────────────────────────────

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
        Generates all fields needed for a PayU payment form.
        The caller (InitiatePaymentView) must supply customer details and callback URLs.
        """
        if not customer:
            raise ValueError("PayU requires customer details (name, email, phone) to create an order.")

        # PayU txnid: alphanumeric, max 25 chars
        txnid = reference_id.replace("-", "")[:25]

        # Amount must be a string with up to 2 decimal places
        amount_str = f"{float(amount):.2f}"

        productinfo = "Gift Card Purchase"
        firstname   = (customer.get("name") or "Customer").split()[0]
        email       = customer.get("email", "")
        phone       = customer.get("phone", "")

        # udf1 carries our internal reference_id for callback lookup
        udf1 = reference_id

        request_hash = self._request_hash(
            txnid=txnid,
            amount=amount_str,
            productinfo=productinfo,
            firstname=firstname,
            email=email,
            udf1=udf1,
        )

        form_fields = {
            "key":         self.key,
            "txnid":       txnid,
            "amount":      amount_str,
            "productinfo": productinfo,
            "firstname":   firstname,
            "email":       email,
            "phone":       phone,
            "surl":        surl,
            "furl":        furl,
            "hash":        request_hash,
            "udf1":        udf1,   # our reference_id — used in callback
            "udf2":        "",
            "udf3":        "",
            "udf4":        "",
            "udf5":        "",
        }

        return PaymentOrderResult(
            gateway_order_id=txnid,
            amount_paise=int(amount * 100),
            currency=currency,
            gateway_key=self.key,
            gateway_type="redirect",
            action_url=self.action_url,
            form_fields=form_fields,
        )

    def verify_payment(self, payload: Dict[str, str]) -> PaymentVerificationResult:
        """
        Verifies the hash in PayU's callback POST.
        PayU sends: mihpayid, status, txnid, amount, productinfo,
                    firstname, email, udf1..udf5, hash, ...
        """
        try:
            received_hash = payload.get("hash", "")
            status        = payload.get("status", "")
            txnid         = payload.get("txnid", "")
            amount        = payload.get("amount", "")
            productinfo   = payload.get("productinfo", "")
            firstname     = payload.get("firstname", "")
            email         = payload.get("email", "")
            udf1          = payload.get("udf1", "")
            udf2          = payload.get("udf2", "")
            udf3          = payload.get("udf3", "")
            udf4          = payload.get("udf4", "")
            udf5          = payload.get("udf5", "")
            mihpayid      = payload.get("mihpayid", "")

            expected_hash = self._response_hash(
                status=status,
                txnid=txnid,
                amount=amount,
                productinfo=productinfo,
                firstname=firstname,
                email=email,
                udf1=udf1, udf2=udf2, udf3=udf3, udf4=udf4, udf5=udf5,
            )

            if expected_hash.lower() != received_hash.lower():
                return PaymentVerificationResult(
                    success=False,
                    gateway_payment_id=mihpayid,
                    error_message="Hash mismatch — possible tampered callback"
                )

            if status.lower() == "success":
                return PaymentVerificationResult(success=True, gateway_payment_id=mihpayid)
            else:
                return PaymentVerificationResult(
                    success=False,
                    gateway_payment_id=mihpayid,
                    error_message=f"Payment {status}: {payload.get('error_message', '')}"
                )

        except Exception as e:
            return PaymentVerificationResult(success=False, gateway_payment_id="", error_message=str(e))
