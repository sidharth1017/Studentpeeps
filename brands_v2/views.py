from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .models import Brand, Offer, OfferSEO, OfferCodeForUser, RedeemedCodes
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import csv
from django.core.files.storage import default_storage
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone

class OfferPageView(View):
    def get(self, request, brand_slug, offer_custom_id):
        brand = get_object_or_404(Brand, slug=brand_slug)
        offers = get_object_or_404(Offer, brand=brand, custom_id=offer_custom_id)
        seo_obj = OfferSEO.objects.filter(offer=offers).first()
        if seo_obj:
            seo = seo_obj
        else:
            seo = SimpleNamespace()
            seo.title = "Student Peeps: Free Student Discounts | Student Deals & Offers"
            seo.description = "Get FREE Student Discounts on your favorite brands like Bewakoof, Rapido Bike Taxi & Bitclass. Student discount for Samsung, Oneplus student discount, Apple Student Discount."
            seo.keywords = "student discounts, brand offers, exclusive student deals"

        seo.og_url = request.build_absolute_uri()
        seo.canonical_url = request.build_absolute_uri(request.path)

        if offers.isLoginRequired:
            redirect_link = offers.offer_link if request.user.is_authenticated and offers.isRedirectLogin and offers.offer_link else None
        else:
            redirect_link = offers.offer_link if offers.isRedirectLogin and offers.offer_link else None

        context = {
            'brand': brand,
            'offer': offers,
            'seo': seo_obj,
            'redirect_offer_link': redirect_link
        }
        return render(request, 'offer/offer_page.html', context)


class GetCodeView(View):
    def get(self, request, brand_slug, offer_custom_id):
        brand = get_object_or_404(Brand, slug=brand_slug)
        offers = get_object_or_404(Offer, brand=brand, custom_id=offer_custom_id)

        if offers.isLoginRequired and not request.user.is_authenticated:
            return redirect(f'/account/v2/identify?next={request.path}')

        seo_obj = OfferSEO.objects.filter(offer=offers).first()
        if seo_obj:
            seo = seo_obj
        else:
            seo = SimpleNamespace()
            seo.title = "Student Peeps: Free Student Discounts | Student Deals & Offers"
            seo.description = "Get FREE Student Discounts on your favorite brands like Bewakoof, Rapido Bike Taxi & Bitclass. Student discount for Samsung, Oneplus student discount, Apple Student Discount."
            seo.keywords = "student discounts, brand offers, exclusive student deals"

        seo.og_url = request.build_absolute_uri()
        seo.canonical_url = request.build_absolute_uri(request.path)

        if offers.isStaticCode:
            code = offers.codes[0] if offers.codes else "OFFER NOT AVAILABLE"
        else:
            if offers.codes:
                code = offers.codes.pop(0)
                offers.save()

                redeemed_obj, created = RedeemedCodes.objects.get_or_create(offer_custom_id=offers.custom_id)

                now = timezone.now().isoformat()
                redeemed_obj.redeemed_codes.append({code: now})
                redeemed_obj.save()
            else:
                code = "OFFER NOT AVAILABLE"


        context = {
            'brand': brand,
            'offer': offers,
            'seo': seo_obj,
            'code': code,
        }

        return render(request, 'offer/get_code_page.html', context)
