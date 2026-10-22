from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.views.generic.base import View
from django.contrib import messages
from .models import Contact, RequestBrand, Foundation, Resource, Brand, Subscribe, Homepage, PolicyPage
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from account.tasks import send_brand_mail, send_course_mail, send_subscribe_email, send_contact_mail
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from account.models import UnVerified
from account.tasks import send_email
import json
from django.contrib.auth.models import User
from brands_v2.models import Offer, Category
import random
from django.db.models import Count
from giftcard.models import ProviderProduct


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
            giftcards = ProviderProduct.objects.filter(
                sku__in=offer_ids,
                in_stock=True
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

        # -------------------------------------------------------------
        # 2. Brand Design Metadata (Palette, Pattern, Discount, Use)
        # -------------------------------------------------------------
        BRAND_CONFIG = {
            'EGVGBPVRC001': {'display': 'PVR INOX', 'discount': 12.0, 'pal': ('#2442E6', '#6440E0'), 'pt': 'p-rings', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBDEGCS001': {'display': "Domino's", 'discount': 4.5, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-stars', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBMYNC001': {'display': 'Myntra', 'discount': 0.75, 'pal': ('#7C3FD6', '#30177D'), 'pt': 'p-waves', 'use': 'Online', 'use_icon': 'i-globe'},
            'EGVGBSTB001': {'display': 'Starbucks', 'discount': 3.75, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-grid', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBUBER001': {'display': 'Uber', 'discount': 1.5, 'pal': ('#2FA8FF', '#2350DB'), 'pt': 'p-lines', 'use': 'Online', 'use_icon': 'i-globe'},
            'EGCGBCROM001': {'display': 'Croma', 'discount': 0.5, 'pal': ('#2442E6', '#6440E0'), 'pt': 'p-grid', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBLVSS001': {'display': "Levi's", 'discount': 5.25, 'pal': ('#C2337A', '#541750'), 'pt': 'p-stars', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBSCLPL002': {'display': 'Lenskart', 'discount': 5.25, 'pal': ('#7C3FD6', '#30177D'), 'pt': 'p-rings', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBCINE001': {'display': 'Cinepolis', 'discount': 16.5, 'pal': ('#7C3FD6', '#30177D'), 'pt': 'p-grid', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBDCN003': {'display': 'Decathlon', 'discount': 2.0, 'pal': ('#3A4160', '#14172F'), 'pt': 'p-rings', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBCCD001': {'display': 'Cafe Coffee Day', 'discount': 6.75, 'pal': ('#E3A866', '#B4602F'), 'pt': 'p-stars', 'use': 'In-store', 'use_icon': 'i-store'},
            'EGVGBKFC001': {'display': 'KFC', 'discount': 2.75, 'pal': ('#E3A866', '#B4602F'), 'pt': 'p-grid', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBPZH001': {'display': 'Pizza Hut', 'discount': 4.5, 'pal': ('#E3A866', '#B4602F'), 'pt': 'p-grid', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBSUBW001': {'display': 'Subway', 'discount': 5.5, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-rings', 'use': 'In-store', 'use_icon': 'i-store'},
            'EGCGBWS002': {'display': 'Westside', 'discount': 5.25, 'pal': ('#7C3FD6', '#30177D'), 'pt': 'p-waves', 'use': 'Online & in-store', 'use_icon': 'i-store'},
            'EGCGBAJIORRL001': {'display': 'AJIO', 'discount': 3.25, 'pal': ('#7C3FD6', '#30177D'), 'pt': 'p-waves', 'use': 'Online', 'use_icon': 'i-globe'},
            'EGCGBGRDM001': {'display': 'Giva Silver Coin', 'discount': 0.75, 'pal': ('#0A7368', '#17BF91'), 'pt': 'p-grid', 'use': 'Online', 'use_icon': 'i-globe'},
            'EGCGBZOMA001': {'display': 'Zomato', 'discount': 2.5, 'pal': ('#FF7457', '#C9302B'), 'pt': 'p-rings', 'use': 'Online', 'use_icon': 'i-globe'},
            'EGCGBBLINK002': {'display': 'Blinkit', 'discount': 2.5, 'pal': ('#17BF91', '#0A7368'), 'pt': 'p-lines', 'use': 'Online', 'use_icon': 'i-globe'},
            'EGCGBBBS001': {'display': 'Bigbasket', 'discount': 1.0, 'pal': ('#7FC93A', '#1F8F57'), 'pt': 'p-zig', 'use': 'Online', 'use_icon': 'i-globe'},
            'EGVGBAPOPHA001': {'display': 'Apollo Pharmacy', 'discount': 5.5, 'pal': ('#C2337A', '#541750'), 'pt': 'p-grid', 'use': 'Online & in-store', 'use_icon': 'i-store'},
        }

        # -------------------------------------------------------------
        # 3. Popular Cards Query
        # -------------------------------------------------------------
        popular_skus = list(BRAND_CONFIG.keys())
        popular_products_qs = ProviderProduct.objects.filter(
            sku__in=popular_skus, in_stock=True
        ).select_related('override', 'override__category')

        popular_products_map = {p.sku: p for p in popular_products_qs}
        popular_cards = []

        for sku in popular_skus:
            prod = popular_products_map.get(sku)
            if not prod:
                continue

            conf = BRAND_CONFIG.get(sku, {})
            disp_brand = conf.get('display') or prod.brand_name or prod.name
            min_p = int(prod.min_price or 100)
            max_p = int(prod.max_price or 5000)

            if min_p == max_p:
                range_txt = f"₹{min_p:,}"
            else:
                range_txt = f"₹{min_p:,}–₹{max_p:,}"

            # Brand length class
            L = len(disp_brand)
            b_cls = 'x3' if L > 30 else 'xxl' if L > 22 else 'xl' if L > 14 else 'long' if L > 9 else ''

            cat_name = "Gift card"
            if hasattr(prod, 'override') and prod.override.category:
                cat_name = prod.override.category.name

            popular_cards.append({
                'sku': prod.sku,
                'name': prod.name,
                'display_brand': disp_brand,
                'brand_size_cls': b_cls,
                'tile_brand_logo_url': prod.tile_brand_logo_url,
                'pal_0': conf.get('pal', ('#2442E6', '#6440E0'))[0],
                'pal_1': conf.get('pal', ('#2442E6', '#6440E0'))[1],
                'pattern_cls': conf.get('pt', 'p-dots'),
                'discount_display': f"{conf.get('discount', 5.0)}%",
                'range_txt': range_txt,
                'category_name': cat_name,
                'use_txt': conf.get('use', 'Online & in-store'),
                'use_icon': conf.get('use_icon', 'i-store'),
                'min_price': min_p,
            })

        # -------------------------------------------------------------
        # 4. Treats Under ₹300
        # -------------------------------------------------------------
        TREATS_SPEC = [
            {'brand_name': 'Starbucks', 'sku': 'EGVGBSTB001', 'tagline': 'A coffee before the paper', 'card_val': 250, 'discount': 3.75, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-grid'},
            {'brand_name': 'Subway', 'sku': 'EGCGBSUBW001', 'tagline': 'Lunch between lectures', 'card_val': 200, 'discount': 5.5, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-rings'},
            {'brand_name': "Domino's", 'sku': 'EGCGBDEGCS001', 'tagline': 'Pizza for the group project', 'card_val': 250, 'discount': 4.5, 'pal': ('#FF9F1C', '#F2542D'), 'pt': 'p-stars'},
            {'brand_name': 'KFC', 'sku': 'EGVGBKFC001', 'tagline': 'Midnight snacks, sorted', 'card_val': 200, 'discount': 2.75, 'pal': ('#E3A866', '#B4602F'), 'pt': 'p-grid'},
            {'brand_name': 'PVR INOX', 'sku': 'EGVGBPVRC001', 'tagline': 'A movie after results', 'card_val': 300, 'discount': 12.25, 'pal': ('#2442E6', '#6440E0'), 'pt': 'p-rings'},
            {'brand_name': 'Cafe Coffee Day', 'sku': 'EGCGBCCD001', 'tagline': 'Thanks for the notes', 'card_val': 100, 'discount': 6.75, 'pal': ('#E3A866', '#B4602F'), 'pt': 'p-stars'},
        ]

        treats_list = []
        for t in TREATS_SPEC:
            disc_amt = t['card_val'] * (t['discount'] / 100.0)
            pay_val = t['card_val'] - disc_amt
            pay_str = f"₹{pay_val:.2f}".rstrip('0').rstrip('.')
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
            })

        # -------------------------------------------------------------
        # 5. Occasions Data
        # -------------------------------------------------------------
        max_discount_pct = max((c.get('discount', 0) for c in BRAND_CONFIG.values()), default=0)
        picks_spec = [
            {'sku': 'EGVGBPVRC001', 'name': 'PVR INOX', 'why': 'Movie nights'},
            {'sku': 'EGCGBMYNC001', 'name': 'Myntra', 'why': 'Fashion'},
            {'sku': 'EGCGBAJIORRL001', 'name': 'AJIO', 'why': 'Fashion'},
            {'sku': 'EGCGBWS002', 'name': 'Westside', 'why': 'Fashion'},
            {'sku': 'EGCGBSCLPL002', 'name': 'Lenskart', 'why': 'Glasses and lenses'},
            {'sku': 'EGCGBGRDM001', 'name': 'Giva Silver Coin', 'why': 'Silver jewellery'},
        ]
        pick_skus = [p['sku'] for p in picks_spec]
        pick_products = {
            p.sku: p for p in ProviderProduct.objects.filter(sku__in=pick_skus).select_related('override')
        }
        hero_picks = []
        sample_amt = 1000

        def _format_pick_inr(amount):
            rounded = round(float(amount) * 100) / 100
            if rounded == int(rounded):
                return f"₹{int(rounded):,}"
            return f"₹{rounded:,.2f}"

        def _format_pick_disc(d):
            d = float(d)
            if d == int(d):
                return f"{int(d)}%"
            return f"{d:g}%"

        def _pick_discount(prod, fallback):
            if prod:
                try:
                    margin = prod.override.margin
                    if margin is not None:
                        from giftcard.services.margin_pricing import margin_as_percent
                        return float(margin_as_percent(margin))
                except Exception:
                    pass
            return float(fallback)

        for spec in picks_spec:
            sku = spec['sku']
            conf = BRAND_CONFIG.get(sku, {})
            prod = pick_products.get(sku) or popular_products_map.get(sku)
            if not conf and not prod:
                continue
            pick_name = spec['name']
            disc = _pick_discount(prod, conf.get('discount', 0))
            pay_val = sample_amt * (1 - disc / 100)
            L = len(pick_name)
            b_cls = 'x3' if L > 30 else 'xxl' if L > 22 else 'xl' if L > 14 else 'long' if L > 9 else ''
            hero_picks.append({
                'sku': sku,
                'name': pick_name,
                'why': spec['why'],
                'discount': disc,
                'discount_display': _format_pick_disc(disc),
                'sample_amt_str': f"₹{sample_amt:,}",
                'pay_str': _format_pick_inr(pay_val),
                'brand_size_cls': b_cls,
                'pal_0': conf.get('pal', ('#2442E6', '#6440E0'))[0],
                'pal_1': conf.get('pal', ('#2442E6', '#6440E0'))[1],
                'pattern_cls': conf.get('pt', 'p-dots'),
            })

        occasions = [
            {'key': 'diwali', 'title': 'Diwali', 'sub': 'Sun, 8 Nov', 'line': 'Lights, mithai, new clothes', 'pal': ('#3B1A8F', '#C2337A'), 'pt': 'p-diya', 'theme_title': 'Shubh Deepavali', 'category': 'festive'},
            {'key': 'bhaidooj', 'title': 'Bhai Dooj', 'sub': 'Tue, 10 Nov', 'line': 'For the sibling who has your back', 'pal': ('#FF7457', '#B32B76'), 'pt': 'p-hearts', 'theme_title': 'Happy Bhai Dooj', 'category': 'family'},
            {'key': 'birthday', 'title': 'Birthdays', 'sub': '', 'line': 'Midnight delivery, sorted', 'pal': ('#FF4F86', '#FF9F1C'), 'pt': 'p-confetti', 'theme_title': 'Happy birthday!', 'category': 'personal'},
            {'key': 'thanks', 'title': 'Thank you', 'sub': '', 'line': 'For notes, rides and favours', 'pal': ('#17BF91', '#0A6578'), 'pt': 'p-waves', 'theme_title': 'Thank you!', 'category': 'gratitude'},
            {'key': 'luck', 'title': 'Exam luck', 'sub': '', 'line': 'Coffee before the paper', 'pal': ('#FF9F1C', '#E2463F'), 'pt': 'p-stars', 'theme_title': 'All the best!', 'category': 'college'},
            {'key': 'congrats', 'title': 'Congrats', 'sub': '', 'line': 'Placements, results, first jobs', 'pal': ('#2442E6', '#7C3FD6'), 'pt': 'p-confetti', 'theme_title': 'You did it!', 'category': 'milestone'},
        ]

        return render(request, "pages/home_page.html", {
            "categories": categories_data,
            "popular_cards": popular_cards,
            "treats": treats_list,
            "occasions": occasions,
            "hero_picks": hero_picks,
            "max_discount_pct": max_discount_pct,
        })
        
class OurStory(View):
    def get(self, request):
        return render(request,'ourstory.html')

class VerificationMessage(View):
    def get(self, request):        
        messages = request.session.get('institution_email')
        return render(request,'verificationmsg.html', {'msg': messages})

    def post(self, request):
        return render(request,'verificationmsg.html')

class GoogleVerifyMessage(View):
    def get(self, request):
        return render(request,'googleverifymessage.html')

    def post(self, request):
        messages = None
        Email = request.POST.get('verify')        
        unverifiedUsers = UnVerified.objects.all()
        for unverifiedUser in unverifiedUsers:
            if unverifiedUser.email == Email or unverifiedUser.institution_email == Email:
                message = render_to_string('mail_body_unverified.html', {'fname': unverifiedUser.firstname, 'lname': unverifiedUser.lastname, 'activate_url': unverifiedUser.verification_url})
                send_email(subject="Sign up karke verify na karna, is not funny!", email=[unverifiedUser.institution_email], message=message)  
                messages = "We've sent you mail on your university email verify yourself!"              
                return render(request,'googleverifymessage.html',{'messages' : messages})

        messages = "You have not signed up yet please do signup!"
        return render(request,'googleverifymessage.html',{'messages' : messages})

class UploadMessage(View):
    def get(self, request):
        return render(request,'uploadmsg.html')

class GoogleVerification(View):
    def get(self, request):
        return render(request,'verified.html')

class UnSubscribe(View):
    def get(self, request):
        return render(request,'unsubscribe.html')

class ContactUs(View):
    def get(self, request):
        messages = None
        return render(request,'contactus.html',{'message' : messages})

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
        return render(request,'contactus.html',{'message' : messages})

class Community(View):
    def get(self, request):
        return render(request,'community.html')

class FAQ(View):
    def get(self, request):
        return render(request,'faq.html')

class Privacy(View):
    def get(self, request):
        return render(request,'privacy.html')

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
                message = render_to_string('mail_body_subscribe.html')
                send_subscribe_email(subject="your community access😎", email=email, message=message)
            except Exception as e:
                print(f"Email sending failed: {e}")

        return HttpResponseRedirect('/')

class UnSubscribeView(View):
    def get(self, request):
        return render(request,'unsubscribe.html')
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
        return render(request, '404.html')

class IdVerificationMessage(View):
    def get(self, request):        
        return render(request,'account/idCardVerification.html')


# Categories for Offers
class CategoryPageView(View):
    def get(self, request, category_id):
        categoryTitle = ""
        if category_id == "exclusive":
            offers = Offer.objects.filter(isExclusive=True).order_by('-sorting')
            category = Category(title="Exclusive Discounts", category_id="exclusive")
            category.meta_title = "Exclusive Discounts for Students - Studentpeeps"
            category.meta_description = "Find exclusive discounts for students on various brands and services."
            category.meta_keywords = "exclusive discounts, student discounts, brand offers"

        elif category_id == "nonexclusive":
            offers = Offer.objects.filter(isExclusive=False).order_by('-sorting')
            category = Category(title="Non-Exclusive Discounts", category_id="nonexclusive")
            category.meta_title = "Non-Exclusive Discounts for Students - Studentpeeps"
            category.meta_description = "Discover non-exclusive discounts for students on various brands and services."
            category.meta_keywords = "non-exclusive discounts, student discounts, brand offers"

        elif category_id == "all":
            offers = Offer.objects.all().order_by('-sorting')
            category = Category(title="All Discounts", category_id="all")
            category.meta_title = "Student Discounts, Offers & Promo Codes for Students | Amazon, Flipkart, Udemy & More – Studentpeeps"
            category.meta_description = "Looking for the best student discounts, coupons, and upcoming sales? At Studentpeeps, we bring you verified offers from top brands so you can save big on tech, fashion, travel, education, and lifestyle. Get exclusive Amazon and Flipkart upcoming sale dates, Big Billion Days, and Great Indian Festival offers, along with today’s deals, promo codes, and coupons tailored for students. Whether you’re hunting for low-price laptops, cheap laptops in India, or the latest generation devices from Lenovo, Dell, Apple, and Samsung, we’ve got you covered. Boost your learning with Udemy’s ₹100 gift card for students and enjoy a free Notion Pro plan to organize your academic life. Explore huge savings on software with Adobe’s 65% student discount and Microsoft Office 365 free for students. Stay entertained with Spotify, YouTube Premium, Apple Music, and Amazon Prime student offers—all at up to 50% off. Refresh your style with Myntra student discounts, DailyObjects smart accessories, Blissclub activewear, and Bacca Bucci sneakers. For travel, grab Etihad, Indigo, Air India, and Lufthansa student flight discounts, making domestic and international trips lighter on your pocket. Studentpeeps is your one-stop student store—a platform where you discover student ID discounts, free coupons, discount codes, and special offers across every category. From Amazon upcoming offers to Flipkart mobile sale dates, we track it all so you never miss a deal. Start saving today with Studentpeeps—the ultimate student benefits hub for India’s smartest learners and trendsetters."
            category.meta_keywords = "student discounts in India, verified student offers, student coupons and promo codes for college and university students, upcoming student sales across Amazon, Flipkart, Udemy and more, best student discount sites in India, top verified deals for students, student savings platform, affordable shopping for students, exclusive student offers and discount codes for every category, verified student deals for college students across tech, fashion, travel, food and education."

        else:
            offers = Offer.objects.filter(category__category_id=category_id).order_by('-sorting')
            category = get_object_or_404(Category, category_id=category_id)

        # Add URLs (works for all because category is always a model object now)
        category.og_url = request.build_absolute_uri()
        category.canonical_url = request.build_absolute_uri(request.path)

        brand_offer_counts = (
            Offer.objects.values('brand')
            .annotate(total=Count('id'))
        )
        brand_offer_map = {item['brand']: item['total'] for item in brand_offer_counts}
        # Add offer flags
        offers_with_flags = []
        for idx, offer in enumerate(offers):
            block_pos = idx % 10
            is_large = block_pos == 0 or block_pos == 6

            if brand_offer_map.get(offer.brand.id, 0) > 1:
                link = f"/brand/{offer.brand.slug}/"
            else:
                link = f"/offer/{offer.brand.slug}/{offer.custom_id}/"
            offer.link = link
            offers_with_flags.append({
                'offer': {
                    'link': link,
                    'title': offer.title,
                    'is_gift_card': False,
                    'thumbnail_image': offer.thumbnail_image,
                    'brand': {
                        'name': offer.brand.name,
                        'logo': offer.brand.logo.url if offer.brand.logo else ""
                    }
                },
                'is_large': is_large,
            })

        carousel_images=[
            "https://website-cdn.xoxoday.com/sales_order_invoice/Diwali%20Deals%201%20Mob.png",
            "https://website-cdn.xoxoday.com/sales_order_invoice/Hotel%20Banner%202%20APP.png",
            "https://website-cdn.xoxoday.com/sales_order_invoice/Diwali%20Deals%201%20Mob.png",
            "https://website-cdn.xoxoday.com/sales_order_invoice/Hotel%20Banner%202%20APP.png"
        ]

        context = {
            'offers': offers_with_flags,
            'heading': category.title,
            'pattern_img': 'images/pattern9.png',
            'category': category,
            'carousel_images': carousel_images
        }
        return render(request, 'pages/category_page.html', context) 

class HelpCenterPageView(View):
    def get(self, request, slug):
        page = get_object_or_404(PolicyPage, slug=slug, status="active")
        page.og_url = request.build_absolute_uri()
        page.canonical_url = request.build_absolute_uri(request.path)
        context = {
            "page": page,
        }

        return render(request, "pages/help_center_page.html", context)


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

        return render(request, "pages/giftcard.html", context)


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

        return render(request, "pages/cart_page.html", context)