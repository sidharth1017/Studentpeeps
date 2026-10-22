"""
Payment methods offered on our checkout.

What the customer sees (which methods, their order, label, description, extra fee %, discount %)
is edited in the admin: Utilities > Payment method options. The code here only holds the
defaults and each method's mapping to a gateway filter.

PayU Hosted Checkout takes `enforce_paymethod`, a pipe-separated list of categories that it will
show (everything else is hidden):
  https://docs.payu.in/v2/docs/enforce-pay-method-or-remove-category

NEFT/RTGS is intentionally not offered: those payments settle later and would come back to our
callback as "pending", so the order would be treated as failed.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

# key -> default label, default description, PayU enforce_paymethod value, icon id, default fee %
PAY_METHODS = {
    "upi":        {"label": "UPI",                 "description": "Google Pay, PhonePe, Paytm or any UPI app", "payu": "upi",                  "icon": "qr",     "fee": "0"},
    "card":       {"label": "Credit / Debit card", "description": "Visa, Mastercard, RuPay",                   "payu": "creditcard|debitcard", "icon": "card",   "fee": "1.5"},
    "netbanking": {"label": "Net banking",         "description": "Pay from your bank account",                "payu": "netbanking",           "icon": "bank",   "fee": "0"},
    "wallet":     {"label": "Wallets",             "description": "Pay with your wallet balance",              "payu": "cashcard",             "icon": "wallet", "fee": "1.25"},
    "emi":        {"label": "EMI",                 "description": "Split into monthly instalments",            "payu": "emi",                  "icon": "cal",    "fee": "0"},
    "paylater":   {"label": "Pay later",           "description": "Buy now, pay later",                        "payu": "bnpl",                 "icon": "clock",  "fee": "0"},
}


def payu_enforce_value(key: Optional[str]) -> str:
    """PayU `enforce_paymethod` string for one of our method keys ('' = don't restrict)."""
    return PAY_METHODS[key]["payu"] if key in PAY_METHODS else ""


def _pct(value) -> Decimal:
    return Decimal(str(value or 0))


def net_percent(option) -> Decimal:
    """Net adjustment in % for a method: positive = extra fee, negative = discount."""
    return _pct(option.fee_percent) - _pct(option.discount_percent)


def adjust_amount(total: Decimal, option) -> Decimal:
    """Amount the customer pays for `total` using this method (rounded to paise, half up)."""
    total = Decimal(str(total))
    adjusted = total + total * net_percent(option) / Decimal(100)
    return adjusted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _method_tag(o, net: Decimal) -> str:
    if net > 0 and o.fee_percent:
        return f"{o.fee_percent.normalize():f}% fee"
    if net < 0 and o.discount_percent:
        return f"{o.discount_percent.normalize():f}% off"
    if net == 0 and o.enabled:
        return "No extra fee"
    return ""


def get_all_methods() -> List[Dict]:
    """
    Every supported payment method in display order (enabled and disabled).
    Used on product page and checkout so customers see the full list.
    """
    from utilities.models import PaymentMethodOption

    PaymentMethodOption.ensure_defaults()
    options = list(PaymentMethodOption.objects.order_by("sort_order", "id"))
    enabled = [o for o in options if o.enabled]
    nets_enabled = [net_percent(o) for o in enabled] if enabled else [Decimal("0")]
    cheapest = min(nets_enabled)
    dearest = max(nets_enabled)

    out = []
    for o in options:
        net = net_percent(o)
        out.append({
            "key": o.method,
            "label": o.display_label,
            "description": o.display_description,
            "icon": PAY_METHODS[o.method]["icon"],
            "fee_percent": o.fee_percent,
            "discount_percent": o.discount_percent,
            "net_percent": net,
            "enabled": o.enabled,
            "tag": _method_tag(o, net),
            "is_best": o.enabled and len(enabled) > 1 and cheapest < dearest and net == cheapest,
        })
    return out


def get_enabled_methods() -> List[Dict]:
    """
    Enabled methods only. Falls back to UPI if everything is switched off.
    """
    enabled = [m for m in get_all_methods() if m["enabled"]]
    if enabled:
        return enabled
    import logging
    from utilities.models import PaymentMethodOption

    logging.getLogger(__name__).warning("All payment methods are disabled; falling back to UPI.")
    PaymentMethodOption.ensure_defaults()
    upi = PaymentMethodOption.objects.get(method="upi")
    net = net_percent(upi)
    return [{
        "key": upi.method,
        "label": upi.display_label,
        "description": upi.display_description,
        "icon": PAY_METHODS[upi.method]["icon"],
        "fee_percent": upi.fee_percent,
        "discount_percent": upi.discount_percent,
        "net_percent": net,
        "enabled": True,
        "tag": _method_tag(upi, net),
        "is_best": True,
    }]


def get_enabled_option(key: Optional[str]):
    """The enabled PaymentMethodOption row for `key`, or None."""
    from utilities.models import PaymentMethodOption
    if not key or key not in PAY_METHODS:
        return None
    PaymentMethodOption.ensure_defaults()
    return PaymentMethodOption.objects.filter(method=key, enabled=True).first()
