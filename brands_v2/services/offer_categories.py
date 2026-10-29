"""Map discount offers to browse categories (Category.category_id values)."""

from brands_v2.models import Category, Offer

OFFER_CATEGORY_BY_CUSTOM_ID = {
    "spxadobe65": "electronics-appliances",
    "spxairindia400": "travel",
    "spxprime50": "entertainment",
    "spxapple10": "electronics-appliances",
    "spxapplemusic50": "entertainment",
    "spxbb5": "fashion-lifestyle",
    "spxblissclub10": "fashion-lifestyle",
    "spxdailyobjects15": "fashion-lifestyle",
    "spxdell7percent": "electronics-appliances",
    "spxetihad10": "travel",
    "spxetihad5": "travel",
    "spxetihadcomp": "travel",
    "hp-india": "electronics-appliances",
    "spxindigo10": "travel",
    "spxlenovo2000": "electronics-appliances",
    "spxlenovo5000": "electronics-appliances",
    "spxlufthansa10": "travel",
    "spxmicrosoft365": "electronics-appliances",
    "spxmyntra300": "fashion-lifestyle",
    "spxnilkamal5": "home-furnishings",
    "spxnotionfree": "electronics-appliances",
    "spxoneplus1500": "electronics-appliances",
    "spxrapido50": "travel",
    "spxsamsung30": "electronics-appliances",
    "spxspotify50": "entertainment",
    "spxwtf25": "food-beverages",
    "spxtbh15": "food-beverages",
    "spxudemy100": "books",
    "spxwix50": "electronics-appliances",
    "spxyoutube40": "entertainment",
}


def assign_offer_categories(*, dry_run=False):
    """Apply OFFER_CATEGORY_BY_CUSTOM_ID to Offer rows."""
    categories = {
        c.category_id: c for c in Category.objects.filter(category_id__in=OFFER_CATEGORY_BY_CUSTOM_ID.values())
    }
    others = Category.objects.filter(category_id="others").first()

    updated = 0
    missing_category = []
    unmapped_offers = []

    for offer in Offer.objects.select_related("category"):
        target_id = OFFER_CATEGORY_BY_CUSTOM_ID.get(offer.custom_id)
        if not target_id:
            unmapped_offers.append(offer.custom_id)
            target = others
        else:
            target = categories.get(target_id)
            if not target:
                missing_category.append(target_id)
                target = others

        if target and offer.category_id != target.pk:
            if not dry_run:
                offer.category = target
                offer.save(update_fields=["category"])
            updated += 1

    return {
        "updated": updated,
        "missing_category": missing_category,
        "unmapped_offers": unmapped_offers,
    }
