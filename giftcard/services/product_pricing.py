"""
Gift card face-value rules aligned with Woohoo RANGE vs SLAB pricing.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from giftcard.models import ProviderProduct

DEFAULT_PRESET_VALUES = (100, 250, 500, 1000, 2000, 5000)


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


def allow_custom_amount(product: ProviderProduct) -> bool:
    return effective_price_type(product) == "RANGE"


def _default_presets(min_p: int, max_p: int, limit: int = 5) -> list[int]:
    picked = [v for v in DEFAULT_PRESET_VALUES if min_p <= v <= max_p]
    if min_p not in picked and min_p > 0:
        picked.insert(0, min_p)
    if max_p not in picked and max_p > min_p:
        picked.append(max_p)
    picked = sorted(set(picked))
    if len(picked) <= limit:
        return picked
    # Keep min, max, and spread middle values
    if limit < 2:
        return picked[:limit]
    step = max(1, (len(picked) - 1) // (limit - 1))
    sparse = [picked[i] for i in range(0, len(picked), step)]
    if picked[-1] not in sparse:
        sparse[-1] = picked[-1]
    return sorted(set(sparse))[:limit]


def amount_choices(product: ProviderProduct, *, max_buttons: int = 6) -> list[int]:
    min_p, max_p = bounds(product)
    if min_p <= 0 or max_p <= 0 or min_p > max_p:
        return []

    ptype = effective_price_type(product)
    denoms = [d for d in denomination_ints(product) if min_p <= d <= max_p]

    if ptype == "SLAB":
        return denoms if denoms else ([min_p] if min_p == max_p else [])

    if denoms:
        if len(denoms) <= max_buttons:
            return denoms
        return _default_presets(min_p, max_p, max_buttons)

    return _default_presets(min_p, max_p, max_buttons)


def default_amount(product: ProviderProduct) -> int:
    choices = amount_choices(product)
    if choices:
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
        allowed = denomination_ints(product)
        if allowed and value not in allowed:
            allowed_text = ", ".join(f"₹{a:,}" for a in allowed[:8])
            suffix = "…" if len(allowed) > 8 else ""
            return False, f"This card is only available in fixed amounts: {allowed_text}{suffix}."

    return True, None


def pricing_config_for_product(product: ProviderProduct) -> dict:
    min_p, max_p = bounds(product)
    choices = amount_choices(product)
    ptype = effective_price_type(product)
    return {
        "price_type": ptype,
        "min_price": min_p,
        "max_price": max_p,
        "denominations": denomination_ints(product),
        "amount_choices": choices,
        "default_amount": default_amount(product),
        "allow_custom_amount": allow_custom_amount(product),
    }
