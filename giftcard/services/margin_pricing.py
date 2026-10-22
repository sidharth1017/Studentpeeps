from decimal import Decimal


def margin_as_percent(margin) -> Decimal:
    """
    Margin as percent off face value for UPI pricing.
    Positive → customer pays less; negative → customer pays more than face value.
    Stored values are always literal percents (0.5 → 0.5%, 16.5 → 16.5%).
    """
    if margin is None:
        return Decimal("0")
    return Decimal(str(margin))


def margin_adjustment(unit_price, margin) -> Decimal:
    """Amount subtracted from face value (negative → surcharge)."""
    unit_price = Decimal(str(unit_price))
    pct = margin_as_percent(margin)
    return (unit_price * pct) / Decimal("100")


def price_after_margin(unit_price, margin) -> Decimal:
    return Decimal(str(unit_price)) - margin_adjustment(unit_price, margin)
