from brands_v2.models import Category

from giftcard.models import Cart
from giftcard.services.cart_service import CartService
from main.services.homepage_merchandising import active_promo_strip

# Same five categories as the gift-card prototype header (slug order).
SUBNAV_CATEGORY_SLUGS = (
    "food-beverages",
    "fashion-lifestyle",
    "entertainment",
    "e-commerce",
    "travel",
)


def _promo_strip():
    try:
        return active_promo_strip()
    except Exception:
        return {"promo_strip_visible": False}


def subnav_categories(request):
    by_slug = {
        c.category_id: c
        for c in Category.objects.filter(isVisible=True, category_id__in=SUBNAV_CATEGORY_SLUGS)
    }
    ordered = [by_slug[slug] for slug in SUBNAV_CATEGORY_SLUGS if slug in by_slug]

    active_category = ""
    if request.path.rstrip("/").endswith("/giftcard/explore"):
        raw = (request.GET.get("category") or "all").strip()
        active_category = raw if raw else "all"

    return {
        "subnav_categories": ordered,
        "subnav_active_category": active_category,
    }


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
