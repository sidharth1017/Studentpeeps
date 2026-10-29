from django.db.models import Q


def sellable_giftcard_q() -> Q:
    """
    Provider products eligible for storefront listing.
    Excludes Woohoo out-of-stock and overrides with status unchecked (NOT LIVE).
    """
    return Q(in_stock=True) & (
        Q(override__isnull=True) | Q(override__status=True)
    )
