from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect
from django.views.generic.base import View
from django.contrib import messages
from .models import Contact, Foundation, Resource, Subscribe, Homepage, PolicyPage
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts_v2.tasks import send_subscribe_email, send_contact_mail
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from brands_v2.models import Offer, Category
import random
from django.db.models import Count, Q
from giftcard.models import ProviderProduct


def brand_offer_count_map():
    rows = Offer.objects.values("brand").annotate(total=Count("id"))
    return {row["brand"]: row["total"] for row in rows}


def offer_detail_link(offer, brand_offer_map):
    if brand_offer_map.get(offer.brand_id, 0) > 1:
        return f"/brand/{offer.brand.slug}/"
    return f"/offer/{offer.brand.slug}/{offer.custom_id}/"


def offer_as_tile(offer, brand_offer_map):
    logo = offer.brand.logo.url if offer.brand.logo else ""
    thumb = offer.thumbnail_image.url if offer.thumbnail_image else ""
    return {
        "link": offer_detail_link(offer, brand_offer_map),
        "title": offer.title,
        "subtitle": offer.subtitle,
        "brand_name": offer.brand.name,
        "brand_logo": logo,
        "thumbnail_url": thumb,
        "is_exclusive": offer.isExclusive,
    }


# Create your views here.
@method_decorator(csrf_exempt, name="dispatch")
# class Home(View):
#     def get(self, request):
#         recommended_offer_ids = ['spxdailyobjects15', 'spxdell7percent','spxnilkamal5', 'spxblissclub10', 'spxbb6', 'spxwtf25']
#         recommended_offers = Offer.objects.filter(custom_id__in=recommended_offer_ids)
#         offers_dict = {offer.custom_id: offer for offer in recommended_offers}
#         ordered_recommended = [offers_dict[oid] for oid in recommended_offer_ids if oid in offers_dict]

#         brand_offer_counts = (
#             Offer.objects.values('brand')
#             .annotate(total=Count('id'))
#         )
#         brand_offer_map = {item['brand']: item['total'] for item in brand_offer_counts}

#         recommended_with_flags = []
#         for idx, offer in enumerate(ordered_recommended):
#             block_pos = idx % 10
#             is_large = block_pos == 0 or block_pos == 6
#             if brand_offer_map.get(offer.brand.id, 0) > 1:
#                 link = f"/brand/{offer.brand.slug}/"
#             else:
#                 link = f"/offer/{offer.brand.slug}/{offer.custom_id}/"
#             offer.link = link
#             recommended_with_flags.append({
#                 'offer': offer,
#                 'is_large': is_large
#             })

#         all_offers = list(Offer.objects.all())
#         featured_sample = random.sample(all_offers, min(15, len(all_offers)))

#         featured_with_flags = []
#         for idx, offer in enumerate(featured_sample):
#             block_pos = idx % 10
#             is_large = block_pos == 0 or block_pos == 6
#             if brand_offer_map.get(offer.brand.id, 0) > 1:
#                 link = f"/brand/{offer.brand.slug}/"
#             else:
#                 link = f"/offer/{offer.brand.slug}/{offer.custom_id}/"
#             offer.link = link
#             featured_with_flags.append({
#                 'offer': offer,
#                 'is_large': is_large
#             })


        # carousel_images=[
        #     "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/carousel/3.jpg",
        #     "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/carousel/4.jpg",
        #     "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/carousel/5.jpg",
        #     "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/carousel/6.jpg",
        #     "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/carousel/7.jpg",
        #     "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/carousel/8.jpg",
        #     "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/carousel/9.jpg",
        # ]

#         return render(request, 'pages/home_page.html', {
#             'recommended_offers': recommended_with_flags,
#             'featured_offers': featured_with_flags,
#             'carousel_images': carousel_images,
#             'category_section': {
#                 'title': 'Top Categories',
#                 'slider': [
#                     {
#                         'image_url': "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/v2/category/gifts_for_her.png",
#                         'category_name': "Gifts for Her"
#                     },
#                     {
#                         'image_url': "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/v2/category/gifts_for_him.png",
#                         'category_name': "Gifts for Him"
#                     },
#                     {
#                         'image_url': "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/v2/category/genz.png",
#                         'category_name': "GenZ Cool"
#                     },
#                     {
#                         'image_url': "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/v2/category/weekend.png",
#                         'category_name': "Foodies, Fun & Weekend Vibes"
#                     },
#                     {
#                         'image_url': "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/v2/category/travel.png",
#                         'category_name': "Travel, Staycations & Big Moments"
#                     },
#                     {
#                         'image_url': "https://vc-thumbnails.blr1.cdn.digitaloceanspaces.com/studentpeeps/v2/category/luxe.png",
#                         'category_name': "Premium & Luxe Gifting"
#                     }
#                 ]
#             }
#         })

#     def post(self, request):
#         body = json.loads(request.body)
#         if body.get("free"):
#             payment = Payment.objects.filter(user=request.user)[0]
#             payment.payment_status = 1
#             payment.amount = 0.0
#             payment.save()
#             messages.success(request, "You are now member of Studentpeeps!!")
#         return JsonResponse({"message": "Done!"})

class Home(View):
    def build_tile_slider(self, block):
        data = block.data or {}

        offer_ids = data.get("offer_ids", [])
        title = data.get("title", "")
        is_discount = data.get("is_discount", False)

        processed = []
        if is_discount:
            offers = Offer.objects.filter(custom_id__in=offer_ids)
            offers_map = {o.custom_id: o for o in offers}
            ordered_offers = [
                offers_map[oid] for oid in offer_ids if oid in offers_map
            ]

            brand_offer_counts = (
                Offer.objects.values("brand")
                .annotate(total=Count("id"))
            )
            brand_offer_map = {
                i["brand"]: i["total"] for i in brand_offer_counts
            }

            for offer in ordered_offers:
                if brand_offer_map.get(offer.brand.id, 0) > 1:
                    link = f"/brand/{offer.brand.slug}/"
                else:
                    link = f"/offer/{offer.brand.slug}/{offer.custom_id}/"

                processed.append({
                    "is_gift_card": False,
                    "link": link,
                    "thumbnail": offer.thumbnail_image.url if offer.thumbnail_image else "",
                    "title": offer.title,
                    "brand": {
                        "name": offer.brand.name,
                        "logo": offer.brand.logo.url if offer.brand.logo else ""
                    }
                })

        # -----------------------------
        # GIFTCARDS (ProviderProduct)
        # -----------------------------
        else:
            from giftcard.services.catalog_visibility import sellable_giftcard_q

            giftcards = ProviderProduct.objects.filter(
                sellable_giftcard_q(),
                sku__in=offer_ids,
            )
            giftcard_map = {g.sku: g for g in giftcards}
            ordered_giftcards = [
                giftcard_map[sku] for sku in offer_ids if sku in giftcard_map
            ]

            for giftcard in ordered_giftcards:
                # Get pricing data
                min_p = float(giftcard.min_price)
                margin = 0
                margin_val = None
                if hasattr(giftcard, 'override') and giftcard.override.margin is not None:
                    margin_val = giftcard.override.margin

                from giftcard.services.margin_pricing import margin_as_percent, price_after_margin

                margin_pct = float(margin_as_percent(margin_val)) if margin_val is not None else 0.0
                
                # Check for colors - for now we use a default but could be expanded
                bg_color = '#111827' # Default dark for premium look
                
                processed.append({
                    "is_gift_card": True,
                    "link": f"/giftcard/{giftcard.sku}/",
                    "thumbnail": giftcard.brand_logo or giftcard.base_image,
                    "title": giftcard.name,
                    "brand": {
                        "name": giftcard.brand_name,
                        "logo": giftcard.brand_logo
                    },
                    "background_color": bg_color,
                    "secondary_color": bg_color,
                    "text_color": "#ffffff",
                    "min_price": int(min_p),
                    "margin": margin_pct,
                    "final_price": int(price_after_margin(min_p, margin_val)),
                    "sku": giftcard.sku
                })

        return {
            "title": title,
            "is_discount": is_discount,
            "offers": processed
        }

    def get(self, request):
        from giftcard.models import ProviderProduct, ProductOverride
        from brands_v2.models import Category
        from decimal import Decimal

        # -------------------------------------------------------------
        # 1. Categories with SVG sprite icons
        # -------------------------------------------------------------
        cat_icon_map = {
            'food-beverages': 'i-cup',
            'food_drink': 'i-cup',
            'fashion-lifestyle': 'i-shirt',
            'fashion': 'i-shirt',
            'entertainment': 'i-ticket',
            'e-commerce': 'i-bag',
            'shopping': 'i-bag',
            'travel': 'i-suitcase',
            'health-beauty': 'i-heart',
            'electronics-appliances': 'i-headphones',
            'tech': 'i-headphones',
            'gaming': 'i-gamepad',
            'grocery': 'i-basket',
            'sportswear-footwear': 'i-shoe',
            'sports': 'i-shoe',
            'books': 'i-book',
            'home-furnishings': 'i-sofa',
            'home-needs': 'i-home',
            'jewellery': 'i-gem',
            'luxury-brands': 'i-sparkle',
            'others': 'i-tag',
        }

        db_categories = list(Category.objects.all().order_by('sorting'))
        categories_data = []
        for c in db_categories:
            slug = c.category_id or ''
            icon = cat_icon_map.get(slug, cat_icon_map.get(slug.lower().replace(' ', '-'), 'i-tag'))
            categories_data.append({
                'id': c.id,
                'name': c.name,
                'category_id': slug,
                'icon': icon,
            })

        from giftcard.brand_design import BRAND_CONFIG
        from main.services.homepage_merchandising import (
            _load_products,
            build_hero_picks,
            build_popular_cards,
            max_brand_discount_pct,
        )

        hero_section, hero_picks = build_hero_picks()
        popular_section, popular_cards = build_popular_cards()

        # -------------------------------------------------------------
        # 2. Treats Under ₹300
        # -------------------------------------------------------------
        TREATS_SPEC = [
            {'brand_name': 'Starbucks', 'sku': 'EGVGBSTB001', 'tagline': 'A coffee before the paper', 'card_val': 250, 'discount': 3.75, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-grid'},
            {'brand_name': 'Subway', 'sku': 'EGCGBSUBW001', 'tagline': 'Lunch between lectures', 'card_val': 200, 'discount': 5.5, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-rings'},
            {'brand_name': "Domino's", 'sku': 'EGCGBDEGCS001', 'tagline': 'Pizza for the group project', 'card_val': 250, 'discount': 4.5, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-stars'},
            {'brand_name': 'KFC', 'sku': 'EGVGBKFC001', 'tagline': 'Midnight snacks, sorted', 'card_val': 200, 'discount': 2.75, 'pal': ('#E3A866', '#B4602F'), 'pt': 'p-grid'},
            {'brand_name': 'PVR INOX', 'sku': 'EGVGBPVRC001', 'tagline': 'A movie after results', 'card_val': 300, 'discount': 12.25, 'pal': ('#2442E6', '#6440E0'), 'pt': 'p-rings'},
            {'brand_name': 'Cafe Coffee Day', 'sku': 'EGCGBCCD001', 'tagline': 'Thanks for the notes', 'card_val': 100, 'discount': 6.75, 'pal': ('#E3A866', '#B4602F'), 'pt': 'p-stars'},
        ]

        treat_products = _load_products([t['sku'] for t in TREATS_SPEC])
        treats_list = []
        for t in TREATS_SPEC:
            disc_amt = t['card_val'] * (t['discount'] / 100.0)
            pay_val = t['card_val'] - disc_amt
            pay_str = f"₹{pay_val:.2f}".rstrip('0').rstrip('.')
            prod = treat_products.get(t['sku'])
            logo_url = prod.tile_brand_logo_url if prod else ""
            treats_list.append({
                'sku': t['sku'],
                'display_brand': t['brand_name'],
                'tagline': t['tagline'],
                'card_val': t['card_val'],
                'card_value_str': f"₹{t['card_val']:,}",
                'pay_price_str': pay_str,
                'pal_0': t['pal'][0],
                'pal_1': t['pal'][1],
                'pattern_cls': t['pt'],
                'tile_brand_logo_url': logo_url or "",
            })

        # -------------------------------------------------------------
        # Wallet promo (homepage demo cards)
        # -------------------------------------------------------------
        WALLET_PROMO_SPEC = [
            {
                'sku': 'EGCGBMYNC001',
                'name': 'Myntra',
                'pill_label': 'Expires in 18 days',
                'pill_class': 'a',
            },
            {
                'sku': '',
                'resolve_brand': 'BookMyShow',
                'name': 'BookMyShow',
                'pal': ('#FF7457', '#C9302B'),
                'pill_label': 'Valid till Apr 2027',
                'pill_class': '',
            },
            {
                'sku': 'EGVGBSTB001',
                'name': 'Starbucks',
                'pill_label': 'Valid till Jun 2026',
                'pill_class': 'b',
            },
        ]
        from giftcard.services.catalog_visibility import sellable_giftcard_q

        wallet_skus = [s['sku'] for s in WALLET_PROMO_SPEC if s.get('sku')]
        wallet_products = _load_products(wallet_skus)
        wallet_promo_cards = []
        for spec in WALLET_PROMO_SPEC:
            prod = wallet_products.get(spec['sku']) if spec.get('sku') else None
            if not prod and spec.get('resolve_brand'):
                prod = (
                    ProviderProduct.objects.filter(
                        sellable_giftcard_q(),
                        brand_name__icontains=spec['resolve_brand'],
                    )
                    .select_related('override', 'override__category')
                    .first()
                )
            conf = BRAND_CONFIG.get(spec.get('sku') or '', {})
            pal = spec.get('pal') or conf.get('pal', ('#2442E6', '#6440E0'))
            logo_url = prod.tile_brand_logo_url if prod else ""
            wallet_promo_cards.append({
                'name': spec['name'],
                'pill_label': spec.get('pill_label', ''),
                'pill_class': spec.get('pill_class', ''),
                'pal_0': pal[0],
                'pal_1': pal[1],
                'tile_brand_logo_url': logo_url or "",
            })

        max_discount_pct = max_brand_discount_pct()

        occasions = [
            {'key': 'diwali', 'title': 'Diwali', 'sub': 'Sun, 8 Nov', 'line': 'Lights, mithai, new clothes', 'pal': ('#3B1A8F', '#C2337A'), 'pt': 'p-diya', 'theme_title': 'Shubh Deepavali', 'category': 'festive'},
            {'key': 'bhaidooj', 'title': 'Bhai Dooj', 'sub': 'Tue, 10 Nov', 'line': 'For the sibling who has your back', 'pal': ('#FF7457', '#B32B76'), 'pt': 'p-hearts', 'theme_title': 'Happy Bhai Dooj', 'category': 'family'},
            {'key': 'birthday', 'title': 'Birthdays', 'sub': '', 'line': 'Midnight delivery, sorted', 'pal': ('#FF4F86', '#FF9F1C'), 'pt': 'p-confetti', 'theme_title': 'Happy birthday!', 'category': 'personal'},
            {'key': 'thanks', 'title': 'Thank you', 'sub': '', 'line': 'For notes, rides and favours', 'pal': ('#17BF91', '#0A6578'), 'pt': 'p-waves', 'theme_title': 'Thank you!', 'category': 'gratitude'},
            {'key': 'luck', 'title': 'Exam luck', 'sub': '', 'line': 'Coffee before the paper', 'pal': ('#FF9F1C', '#E2463F'), 'pt': 'p-stars', 'theme_title': 'All the best!', 'category': 'college'},
            {'key': 'congrats', 'title': 'Congrats', 'sub': '', 'line': 'Placements, results, first jobs', 'pal': ('#2442E6', '#7C3FD6'), 'pt': 'p-confetti', 'theme_title': 'You did it!', 'category': 'milestone'},
        ]

        return render(request, "pages/home.html", {
            "categories": categories_data,
            "popular_cards": popular_cards,
            "popular_section": popular_section,
            "treats": treats_list,
            "occasions": occasions,
            "hero_picks": hero_picks,
            "hero_section": hero_section,
            "wallet_promo_cards": wallet_promo_cards,
            "max_discount_pct": max_discount_pct,
        })
        
class OurStory(View):
    def get(self, request):
        return render(request, "marketing/our_story.html")

class UploadMessage(View):
    def get(self, request):
        return render(request,'uploadmsg.html')

class UnSubscribe(View):
    def get(self, request):
        return render(request, "marketing/newsletter_unsubscribe.html")

class ContactUs(View):
    def get(self, request):
        messages = None
        return render(request, "marketing/contact.html", {"message": messages})

    def post(self, request):
        messages = None
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        contact = Contact(name=name, email=email, message=message)
        contact.save()

        try:
            subject = f"Somebody Contacted Us"
            send_contact_mail(subject, name, email, message, ["hi@studentpeeps.club"])
        except Exception as e:
            print(f"Email sending failed: {e}")

        messages = "Thanks for contacting us, we'll reach out you soon."
        return render(request, "marketing/contact.html", {"message": messages})

class Community(View):
    def get(self, request):
        return render(request,'community.html')

class SubscribeView(View):
    def post(self, request):
        email = request.POST.get('subscribe_email')
        if Subscribe.objects.filter(email=email).exists():
            messages.success(request, "Thanks for subscribing to the Studentpeeps' community! We'll be sure to send you exclusive offers and deals straight to your inbox😊")
        else:
            subscribe = Subscribe(email=email)
            subscribe.save()
            messages.success(request, "Thanks for subscribing to the Studentpeeps' community! We'll be sure to send you exclusive offers and deals straight to your inbox😊")
            try:
                message = render_to_string('emailers/subscribe_email_body.html')
                send_subscribe_email(subject="your community access😎", email=email, message=message)
            except Exception as e:
                print(f"Email sending failed: {e}")

        return HttpResponseRedirect('/')

class UnSubscribeView(View):
    def get(self, request):
        return render(request, "marketing/newsletter_unsubscribe.html")
    def post(self, request):
        email = request.POST.get('unsubscribe_email')
        if Subscribe.objects.filter(email=email).exists():
            Subscribe.objects.filter(email=email).delete()
            messages.info(request, "You are UnSubscribed to our Newsletters!")
        else:
            messages.info(request, "You are not our Subscriber!")
        return HttpResponseRedirect('/')
        
class Error_404_View(View):
    def get(self, request):
        return render(request, "errors/not_found.html")

class IdVerificationMessage(View):
    def get(self, request):        
        return render(request, "pages/account/id_verification_success.html")


class DiscountsPageView(View):
    """Student discount coupons & promo codes (legacy offers hub, new UI)."""

    def get(self, request):
        from main.services.discount_home import build_discount_home_context

        all_offers = list(
            Offer.objects.select_related("brand", "category").order_by("-sorting")
        )
        featured_sample = random.sample(all_offers, min(12, len(all_offers)))
        home_ctx = build_discount_home_context(featured_sample=featured_sample)

        context = {
            "offer_count": len(all_offers),
            "canonical_url": request.build_absolute_uri(request.path),
            **home_ctx,
        }
        return render(request, "pages/discounts/list.html", context)


class DiscountExploreView(View):
    """Browse/filter student discount offers — mirrors giftcard ExploreView."""

    CATEGORY_META = {
        "fashion": {"icon": "shirt", "color": "#ff4d4d"},
        "tech": {"icon": "smartphone", "color": "#4d79ff"},
        "travel": {"icon": "plane", "color": "#4dff88"},
        "food_drink": {"icon": "utensils-crossed", "color": "#ffb347"},
        "health_beauty": {"icon": "sparkles", "color": "#ff66b2"},
        "home_utilities": {"icon": "home", "color": "#9966ff"},
        "education": {"icon": "graduation-cap", "color": "#4da6ff"},
        "entertainment": {"icon": "play", "color": "#ff4d4d"},
        "exclusive": {"icon": "sparkles", "color": "#6440E0"},
        "nonexclusive": {"icon": "tag", "color": "#17BF91"},
    }

    ACCESS_FILTERS = [
        {"id": "exclusive", "label": "Exclusive offers"},
        {"id": "open", "label": "Open to everyone"},
    ]

    def _offer_count_for_category(self, category_id):
        if category_id == "exclusive":
            return Offer.objects.filter(isExclusive=True).count()
        if category_id == "nonexclusive":
            return Offer.objects.filter(isExclusive=False).count()
        if category_id == "all":
            return Offer.objects.count()
        return Offer.objects.filter(category__category_id=category_id).count()

    def _selected_category_label(self, category_id):
        if category_id == "all":
            return "All offers"
        if category_id == "exclusive":
            return "Exclusive offers"
        if category_id == "nonexclusive":
            return "Non-exclusive offers"
        cat = Category.objects.filter(category_id=category_id).first()
        if cat:
            return cat.name
        return category_id.replace("_", " ").replace("-", " ").title()

    def get(self, request):
        query = request.GET.get("search", "")
        category_id = request.GET.get("category", "all")
        sort_by = request.GET.get("sort", "popular")
        selected_access = request.GET.getlist("price_range")

        offers_qs = Offer.objects.select_related("brand", "category")

        if query:
            offers_qs = offers_qs.filter(
                Q(title__icontains=query)
                | Q(subtitle__icontains=query)
                | Q(brand__name__icontains=query)
            )

        if category_id == "exclusive":
            offers_qs = offers_qs.filter(isExclusive=True)
        elif category_id == "nonexclusive":
            offers_qs = offers_qs.filter(isExclusive=False)
        elif category_id != "all":
            offers_qs = offers_qs.filter(category__category_id=category_id)

        if selected_access:
            access_q = Q()
            for access_id in selected_access:
                if access_id == "exclusive":
                    access_q |= Q(isExclusive=True)
                elif access_id == "open":
                    access_q |= Q(isExclusive=False)
            if access_q:
                offers_qs = offers_qs.filter(access_q)

        if sort_by == "name":
            offers_qs = offers_qs.order_by("brand__name", "title")
        elif sort_by == "price-low":
            offers_qs = offers_qs.order_by("title")
        elif sort_by == "price-high":
            offers_qs = offers_qs.order_by("-title")
        else:
            offers_qs = offers_qs.order_by("-sorting")

        brand_offer_map = brand_offer_count_map()
        filtered_count = offers_qs.count()
        offers = [offer_as_tile(o, brand_offer_map) for o in offers_qs]

        all_categories = list(
            Category.objects.filter(isVisible=True, offers__isnull=False)
            .distinct()
            .order_by("sorting")
        )
        total_count = Offer.objects.count()

        categories_with_meta = []
        for special_id, special_name in (
            ("exclusive", "Exclusive"),
            ("nonexclusive", "Non-exclusive"),
        ):
            meta = self.CATEGORY_META.get(special_id, {"icon": "sparkles", "color": "#3b82f6"})
            cat_qd = request.GET.copy()
            cat_qd["category"] = special_id
            categories_with_meta.append(
                {
                    "id": special_id,
                    "name": special_name,
                    "icon": meta["icon"],
                    "color": meta["color"],
                    "count": self._offer_count_for_category(special_id),
                    "url": "?" + cat_qd.urlencode(),
                }
            )

        for cat in all_categories:
            meta = self.CATEGORY_META.get(
                cat.category_id, {"icon": "sparkles", "color": "#3b82f6"}
            )
            cat_qd = request.GET.copy()
            cat_qd["category"] = cat.category_id
            categories_with_meta.append(
                {
                    "id": cat.category_id,
                    "name": cat.name,
                    "icon": meta["icon"],
                    "color": meta["color"],
                    "count": self._offer_count_for_category(cat.category_id),
                    "url": "?" + cat_qd.urlencode(),
                }
            )

        all_brands_qd = request.GET.copy()
        all_brands_qd["category"] = "all"
        all_brands_url = "?" + all_brands_qd.urlencode()

        sort_urls = {}
        for s in ["popular", "name", "price-low", "price-high"]:
            sort_qd = request.GET.copy()
            sort_qd["sort"] = s
            key = s.replace("-", "_")
            sort_urls[key] = "?" + sort_qd.urlencode()

        price_ranges_meta = []
        for access in self.ACCESS_FILTERS:
            pr_qd = request.GET.copy()
            current_list = pr_qd.getlist("price_range")
            is_selected = access["id"] in current_list
            if is_selected:
                new_list = [x for x in current_list if x != access["id"]]
            else:
                new_list = current_list + [access["id"]]
            pr_qd.setlist("price_range", new_list)
            price_ranges_meta.append(
                {
                    "id": access["id"],
                    "label": access["label"],
                    "selected": is_selected,
                    "url": "?" + pr_qd.urlencode(),
                }
            )

        clear_cat_qd = request.GET.copy()
        clear_cat_qd.pop("category", None)
        clear_category_url = "?" + clear_cat_qd.urlencode()

        clear_search_qd = request.GET.copy()
        clear_search_qd.pop("search", None)
        clear_search_url = "?" + clear_search_qd.urlencode()

        clear_all_url = "?"

        context = {
            "offers": offers,
            "categories": categories_with_meta,
            "all_brands_url": all_brands_url,
            "total_count": total_count,
            "filtered_count": filtered_count,
            "selected_category": category_id,
            "selected_category_label": self._selected_category_label(category_id),
            "search_query": query,
            "sort_by": sort_by,
            "price_ranges": price_ranges_meta,
            "selected_price_ranges": selected_access,
            "sort_urls": sort_urls,
            "clear_category_url": clear_category_url,
            "clear_search_url": clear_search_url,
            "clear_all_url": clear_all_url,
        }
        return render(request, "pages/discounts/explore.html", context)


class DiscountSearchSuggestView(View):
    """Live search suggestions for coupon header / home search (mirrors gift-card suggest API)."""

    TRENDING = ["Spotify", "Myntra", "Dell", "Microsoft", "Indigo", "Rapido"]

    @staticmethod
    def _offer_payload(offer, brand_offer_map):
        from main.services.discount_home import enrich_offer_tile

        tile = enrich_offer_tile(offer, brand_offer_map)
        return {
            "name": tile["brand_name"],
            "title": tile["title"],
            "link": tile["link"],
            "category": tile["category_name"],
            "thumbnail_url": tile["thumbnail_url"] or "",
            "is_exclusive": tile["is_exclusive"],
            "pal_0": tile["pal_0"],
            "pal_1": tile["pal_1"],
            "pattern": tile["pattern_cls"],
            "brand_size_cls": tile["brand_size_cls"],
        }

    def get(self, request):
        q = request.GET.get("q", "").strip()[:60]
        brand_offer_map = brand_offer_count_map()
        qs = Offer.objects.select_related("brand", "category")
        categories = Category.objects.filter(isVisible=True, offers__isnull=False).distinct().order_by("sorting")

        if not q:
            trending, seen = [], set()
            for term in self.TRENDING:
                offer = qs.filter(
                    Q(brand__name__icontains=term)
                    | Q(title__icontains=term)
                    | Q(subtitle__icontains=term)
                ).first()
                if offer and offer.custom_id not in seen:
                    seen.add(offer.custom_id)
                    trending.append(self._offer_payload(offer, brand_offer_map))
            return JsonResponse(
                {
                    "q": q,
                    "brands": trending,
                    "categories": [
                        {
                            "id": c.category_id,
                            "name": c.name,
                            "count": Offer.objects.filter(category=c).count(),
                        }
                        for c in categories
                    ],
                }
            )

        matches = qs.filter(
            Q(title__icontains=q)
            | Q(subtitle__icontains=q)
            | Q(brand__name__icontains=q)
            | Q(category__name__icontains=q)
        )
        ql = q.lower()
        ranked = sorted(
            matches[:60],
            key=lambda o: (
                0 if o.brand.name.lower().startswith(ql) else 1,
                o.brand.name.lower(),
            ),
        )
        offers, seen_brands = [], set()
        for offer in ranked:
            key = offer.brand.name.strip().lower()
            if key in seen_brands:
                continue
            seen_brands.add(key)
            offers.append(offer)
        offers = offers[:8]

        cats = []
        for c in categories.filter(name__icontains=q):
            cats.append(
                {
                    "id": c.category_id,
                    "name": c.name,
                    "count": Offer.objects.filter(category=c).count(),
                }
            )

        return JsonResponse(
            {
                "q": q,
                "brands": [self._offer_payload(o, brand_offer_map) for o in offers],
                "categories": cats,
            }
        )


# Categories for Offers
LEGACY_CATEGORY_SLUGS = {
    "foodsanddrinks": "food_drink",
    "healthandbeauty": "health_beauty",
    "edtech": "education",
    "booksandstationary": "books_stationary",
    "homeandutilities": "home_utilities",
}


class CategoryPageView(View):
    """Legacy /category/<slug>/ URLs → dynamic discount explore (preserves extra query params)."""

    def get(self, request, category_id):
        qd = request.GET.copy()
        qd["category"] = LEGACY_CATEGORY_SLUGS.get(category_id, category_id)
        return redirect(f"/discounts/explore/?{qd.urlencode()}", permanent=True)

HELP_CENTER_TILE_META = {
    "privacy-policy": ("i-shield", "How we collect, use, and protect your information."),
    "refund-policy": ("i-tag", "Refunds, cancellations, and when they apply to gift cards."),
    "terms-and-conditions": ("i-book", "Terms for using StudentPeeps and purchasing gift cards."),
}


class HelpCenterIndexView(View):
    def get(self, request):
        pages = []
        for page in PolicyPage.objects.filter(status="active").order_by("title"):
            icon, blurb = HELP_CENTER_TILE_META.get(
                page.slug,
                ("i-help", "Official guidance and policy from StudentPeeps."),
            )
            page.tile_icon = icon
            page.tile_blurb = blurb
            pages.append(page)
        context = {
            "pages": pages,
            "canonical_url": request.build_absolute_uri(request.path),
        }
        return render(request, "pages/help/index.html", context)


class HelpCenterPageView(View):
    def get(self, request, slug):
        from main.services.policy_content import normalize_policy_html

        page = get_object_or_404(PolicyPage, slug=slug, status="active")
        page.og_url = request.build_absolute_uri()
        page.canonical_url = request.build_absolute_uri(request.path)
        page.content = normalize_policy_html(page.content)
        context = {
            "page": page,
        }

        return render(request, "pages/help/policy.html", context)


class GiftcardView(View):
    def get(self, request):
        context = {
        "page_title": "Amazon Gift Card",
        "amounts": [500, 1000, 2000, 5000],
        "faqs": [
            {
                "question": "What is the validity of the Amazon shopping voucher?",
                "answer": "The Amazon shopping voucher is valid for 1 year."
            },
            {
                "question": "Can I use multiple offers?",
                "answer": "Yes, you can combine offers."
            }
        ],
        "similar_cards": [
            {"name": "ZEPTO", "category": "E-commerce", "offer": "3% off", "color": "bg-purple-700", "initial": "Z"},
            {"name": "Flipkart", "category": "E-commerce", "offer": "1.25% off", "color": "bg-blue-500", "initial": "F"},
        ]
    }

        return render(request, "pages/giftcards/detail.html", context)


class CartView(View):
    def get(self, request):
        context = {
        "page_title": "Amazon Gift Card",
        "amounts": [500, 1000, 2000, 5000],
        "faqs": [
            {
                "question": "What is the validity of the Amazon shopping voucher?",
                "answer": "The Amazon shopping voucher is valid for 1 year."
            },
            {
                "question": "Can I use multiple offers?",
                "answer": "Yes, you can combine offers."
            }
        ],
        "similar_cards": [
            {"name": "ZEPTO", "category": "E-commerce", "offer": "3% off", "color": "bg-purple-700", "initial": "Z"},
            {"name": "Flipkart", "category": "E-commerce", "offer": "1.25% off", "color": "bg-blue-500", "initial": "F"},
        ]
    }

        return render(request, "pages/cart/index.html", context)