from django.urls import reverse

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


def _coupons_nav_mode(request) -> bool:
    path = request.path or ""
    return (
        path.startswith("/discounts")
        or path.startswith("/offer/")
        or path.startswith("/brand/")
    )


def subnav_categories(request):
    by_slug = {
        c.category_id: c
        for c in Category.objects.filter(isVisible=True, category_id__in=SUBNAV_CATEGORY_SLUGS)
    }
    ordered = [by_slug[slug] for slug in SUBNAV_CATEGORY_SLUGS if slug in by_slug]

    coupons_nav = _coupons_nav_mode(request)
    active_category = ""
    path_norm = request.path.rstrip("/")
    if path_norm.endswith("/giftcard/explore"):
        raw = (request.GET.get("category") or "all").strip()
        active_category = raw if raw else "all"
    elif path_norm.endswith("/discounts/explore"):
        raw = (request.GET.get("category") or "all").strip()
        active_category = raw if raw else "all"

    if coupons_nav:
        nav_home_url = reverse("DiscountsPage")
        nav_explore_url = reverse("DiscountExplore")
        nav_search_suggest_url = reverse("DiscountSearchSuggest")
        nav_search_placeholder = "Search Spotify, Myntra, Dell…"
        nav_search_label = "Search coupons"
        nav_product_label = "Coupons"
        subnav_all_label = "All offers"
    else:
        nav_home_url = "/"
        nav_explore_url = reverse("giftcard:explore")
        nav_search_suggest_url = reverse("giftcard:search_suggest")
        nav_search_placeholder = "Search PVR INOX, Myntra, Domino’s…"
        nav_search_label = "Search gift cards"
        nav_product_label = "Gift cards"
        subnav_all_label = "All brands"

    return {
        "subnav_categories": ordered,
        "subnav_active_category": active_category,
        "coupons_nav": coupons_nav,
        "nav_home_url": nav_home_url,
        "nav_explore_url": nav_explore_url,
        "nav_search_suggest_url": nav_search_suggest_url,
        "nav_search_placeholder": nav_search_placeholder,
        "nav_search_label": nav_search_label,
        "nav_product_label": nav_product_label,
        "subnav_all_label": subnav_all_label,
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
