from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .models import ProviderProduct
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import csv
from django.core.files.storage import default_storage
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from types import SimpleNamespace
from giftcard.providers.woohoo.service.product_resolver import ProductResolver

class GiftcardPageView(View):
    def get(self, request, sku):
        # Ensure product exists (404 if not)
        provider_product = get_object_or_404(
            ProviderProduct,
            sku=sku
        )

        # Resolve merged product data
        resolver = ProductResolver(sku)
        giftcard_data = resolver.resolve()

        # ----------------------------------
        # SEO (can later be override-driven)
        # ----------------------------------
        seo = SimpleNamespace()
        seo.title = (
            giftcard_data.get("name")
            or "Student Peeps: Free Student Discounts | Student Deals & Offers"
        )
        seo.description = (
            giftcard_data.get("description")
            or "Get FREE Student Discounts on your favorite brands."
        )
        seo.keywords = "student discounts, brand offers, gift cards"

        seo.og_url = request.build_absolute_uri()
        seo.canonical_url = request.build_absolute_uri(request.path)

        # ----------------------------------
        # CONTEXT
        # ----------------------------------
        print("Giftcard Data:", giftcard_data)  # Debugging log
        context = {
            # merged, frontend-ready data
            "giftcard": giftcard_data,

            # raw provider model (optional, for debugging/admin use)
            "provider_product": provider_product,

            "seo": seo,
        }

        return render(
            request,
            "pages/giftcard_page.html",
            context
        )