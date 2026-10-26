"""
Gift card face-value rules aligned with Woohoo RANGE vs SLAB pricing.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from giftcard.models import ProviderProduct

# Quick-pick amounts on RANGE products (Woohoo allows any value in min–max via Other).
RANGE_UI_PRESETS = (250, 500, 1000, 1500, 2000)
RANGE_UI_TOP_CAP = 5000
MAX_AMOUNT_BUTTONS = 6
RANGE_AMOUNT_STEP = 10


def range_amount_step_message(min_p: int, max_p: int) -> str:
    return (
        f"Use a round amount between ₹{min_p:,} and ₹{max_p:,} "
        f"in steps of ₹{RANGE_AMOUNT_STEP} — for example ₹500 or ₹1,230."
    )


def denomination_ints(product: ProviderProduct) -> list[int]:
    values: list[int] = []
    for raw in product.denominations or []:
        try:
            values.append(int(Decimal(str(raw))))
        except (InvalidOperation, ValueError, TypeError):
            continue
    return sorted(set(values))


def bounds(product: ProviderProduct) -> tuple[int, int]:
    return int(product.min_price or 0), int(product.max_price or 0)


def effective_price_type(product: ProviderProduct) -> str:
    ptype = (product.price_type or "").upper()
    if ptype in ("RANGE", "SLAB"):
        return ptype
    denoms = denomination_ints(product)
    if denoms and bounds(product)[0] == bounds(product)[1] == denoms[0]:
        return "SLAB"
    return "RANGE"


def _standard_chip_candidates(min_p: int, max_p: int) -> list[int]:
    top = min(max_p, RANGE_UI_TOP_CAP)
    candidates = list(RANGE_UI_PRESETS)
    if top not in candidates:
        candidates.append(top)
    return [v for v in candidates if min_p <= v <= max_p]


def allow_custom_amount(product: ProviderProduct) -> bool:
    """Custom entry is only for RANGE. SLAB must use fixed denomination buttons."""
    return effective_price_type(product) == "RANGE"


def purchasable_denominations(product: ProviderProduct) -> list[int]:
    min_p, max_p = bounds(product)
    return [d for d in denomination_ints(product) if min_p <= d <= max_p]


def _range_amount_choices(min_p: int, max_p: int) -> list[int]:
    """
    Fixed chips for RANGE: 250…2000 plus top = min(product max, ₹5000).
    Values outside [min_p, max_p] are dropped.
    """
    choices = _standard_chip_candidates(min_p, max_p)
    if choices:
        return choices[:MAX_AMOUNT_BUTTONS]

    if min_p == max_p:
        return [min_p]
    return [v for v in (min_p, max_p) if v > 0][:MAX_AMOUNT_BUTTONS]


def _slab_amount_choices(allowed: list[int], min_p: int, max_p: int) -> list[int]:
    """All purchasable Woohoo SLAB denominations (no generic presets, no Other)."""
    if allowed:
        return allowed
    return [min_p] if min_p == max_p and min_p > 0 else []


def amount_choices(
    product: ProviderProduct,
    *,
    max_buttons: int = MAX_AMOUNT_BUTTONS,
) -> list[int]:
    min_p, max_p = bounds(product)
    if min_p <= 0 or max_p <= 0 or min_p > max_p:
        return []

    ptype = effective_price_type(product)
    if ptype == "SLAB":
        return _slab_amount_choices(purchasable_denominations(product), min_p, max_p)

    return _range_amount_choices(min_p, max_p)[:max_buttons]


def default_amount(product: ProviderProduct) -> int:
    choices = amount_choices(product)
    if choices:
        if effective_price_type(product) == "RANGE" and 500 in choices:
            return 500
        return choices[0]
    min_p, _ = bounds(product)
    return min_p if min_p > 0 else 100


def validate_denomination(product: ProviderProduct, amount) -> tuple[bool, str | None]:
    try:
        value = int(Decimal(str(amount)))
    except (InvalidOperation, ValueError, TypeError):
        return False, "Enter a valid whole rupee amount."

    if value <= 0:
        return False, "Amount must be greater than zero."

    min_p, max_p = bounds(product)
    if min_p <= 0 or max_p <= 0:
        return False, "This gift card is not available for purchase right now."

    if value < min_p or value > max_p:
        return False, f"Choose an amount between ₹{min_p:,} and ₹{max_p:,}."

    if effective_price_type(product) == "SLAB":
        allowed = purchasable_denominations(product)
        if allowed and value not in allowed:
            allowed_text = ", ".join(f"₹{a:,}" for a in allowed[:8])
            suffix = "…" if len(allowed) > 8 else ""
            return False, f"This card is only available in fixed amounts: {allowed_text}{suffix}."
    elif value % RANGE_AMOUNT_STEP != 0:
        return False, range_amount_step_message(min_p, max_p)

    return True, None


def pricing_config_for_product(product: ProviderProduct) -> dict:
    min_p, max_p = bounds(product)
    choices = amount_choices(product)
    ptype = effective_price_type(product)
    return {
        "price_type": ptype,
        "min_price": min_p,
        "max_price": max_p,
        "denominations": (
            purchasable_denominations(product)
            if ptype == "SLAB"
            else denomination_ints(product)
        ),
        "amount_choices": choices,
        "default_amount": default_amount(product),
        "allow_custom_amount": allow_custom_amount(product),
        "amount_step": RANGE_AMOUNT_STEP if ptype == "RANGE" else 1,
    }
