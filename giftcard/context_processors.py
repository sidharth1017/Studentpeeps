from datetime import date

from brands_v2.models import Category

from giftcard.models import Cart
from giftcard.services.cart_service import CartService

DIWALI_2026 = date(2026, 11, 8)

# Same five categories as the gift-card prototype header (slug order).
SUBNAV_CATEGORY_SLUGS = (
    "food-beverages",
    "fashion-lifestyle",
    "entertainment",
    "e-commerce",
    "travel",
)


def _promo_strip():
    today = date.today()
    days = (DIWALI_2026 - today).days
    if 0 <= days <= 45:
        return {
            "promo_strip_text": "Diwali is on Sunday, 8 November. Schedule gifts to land that morning.",
            "promo_strip_href": "/giftcard/explore/?category=entertainment",
            "promo_strip_link": "Diwali gifts",
        }
    return {
        "promo_strip_text": "Pay with UPI for the best price on every card.",
        "promo_strip_href": "/giftcard/explore/",
        "promo_strip_link": "Browse cards",
    }


def subnav_categories(request):
    by_slug = {
        c.category_id: c
        for c in Category.objects.filter(isVisible=True, category_id__in=SUBNAV_CATEGORY_SLUGS)
    }
    ordered = [by_slug[slug] for slug in SUBNAV_CATEGORY_SLUGS if slug in by_slug]
    return {"subnav_categories": ordered}


def cart_count(request):
    count = 0
    # To avoid creating a session for every anonymous hit, we only query if needed
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if cart and cart.items:
                count = sum(item.get("quantity", 1) for item in cart.items)
        except Exception:
            pass
    elif request.session.session_key:
        try:
            cart = Cart.objects.filter(session_key=request.session.session_key, is_active=True).first()
            if cart and cart.items:
                count = sum(item.get("quantity", 1) for item in cart.items)
        except Exception:
            pass
            
    return {
        "global_cart_count": count,
        **_promo_strip(),
    }
