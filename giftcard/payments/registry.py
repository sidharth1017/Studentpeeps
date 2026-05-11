"""
Gateway Registry
================
Central registry for all payment gateways.
Add new gateways here — no other file needs to change.

Usage:
    from giftcard.payments.registry import get_gateway

    gateway = get_gateway("payu")
    result  = gateway.create_order(...)
"""
from .razorpay_gateway import RazorpayGateway
from .payu_gateway import PayUGateway

GATEWAY_REGISTRY = {
    "razorpay": RazorpayGateway,
    "payu":     PayUGateway,
    # "stripe":    StripeGateway,     # Future
    # "pinelabs":  PineLabsGateway,   # Future
}


def get_gateway(name: str):
    """
    Returns an initialised gateway instance.
    Raises KeyError for unknown gateways.
    """
    cls = GATEWAY_REGISTRY.get(name)
    if not cls:
        raise KeyError(
            f"Unknown payment gateway: '{name}'. "
            f"Available: {list(GATEWAY_REGISTRY.keys())}"
        )
    return cls()
