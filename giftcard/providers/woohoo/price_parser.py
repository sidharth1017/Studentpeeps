"""
Normalize Woohoo catalog price blocks (list + detail API).

Woohoo product detail returns:
  price.type: "RANGE" | "SLAB"
  price.min / price.max: authoritative bounds for orders
  price.denominations: allowed face values (required for SLAB; optional hints for RANGE)

List API only exposes minPrice/maxPrice; type/denominations come from detail sync.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class ParsedWoohooPrice:
    price_type: str | None
    min_price: Decimal
    max_price: Decimal
    denominations: list[str]


def _to_decimal(value: Any) -> Decimal:
    try:
        if value is None or value == "":
            return Decimal("0")
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def _normalize_denominations(raw: Any) -> list[str]:
    if not raw:
        return []
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if item is None or item == "":
            continue
        out.append(str(item))
    return out


def _price_type_from_block(block: dict) -> str | None:
    ptype = block.get("type")
    if ptype in ("RANGE", "SLAB"):
        return ptype
    legacy = block.get("price")
    if legacy in ("RANGE", "SLAB"):
        return legacy
    return None


def _pick_cpg_block(price: dict) -> dict:
    """Legacy list API nests type/denominations under price.cpg."""
    cpg = price.get("cpg")
    if isinstance(cpg, dict):
        for value in cpg.values():
            if isinstance(value, dict) and (
                value.get("type") or value.get("denominations")
            ):
                return value
    return price


def parse_woohoo_product_price(
    price: Any,
    *,
    list_min: Any = None,
    list_max: Any = None,
) -> ParsedWoohooPrice:
    """
    Parse Woohoo ``price`` object from product detail (or list row when populated).
    Falls back to list minPrice/maxPrice when detail min/max are missing.
    """
    if not isinstance(price, dict):
        return ParsedWoohooPrice(
            price_type=None,
            min_price=_to_decimal(list_min),
            max_price=_to_decimal(list_max),
            denominations=[],
        )

    block = _pick_cpg_block(price)
    ptype = _price_type_from_block(block)

    min_price = _to_decimal(block.get("min") or list_min)
    max_price = _to_decimal(block.get("max") or list_max)
    if min_price <= 0 and list_min is not None:
        min_price = _to_decimal(list_min)
    if max_price <= 0 and list_max is not None:
        max_price = _to_decimal(list_max)

    return ParsedWoohooPrice(
        price_type=ptype,
        min_price=min_price,
        max_price=max_price,
        denominations=_normalize_denominations(block.get("denominations")),
    )
