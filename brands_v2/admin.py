from django.contrib import admin
from .models import Brand, Offer, OfferSEO, OfferCodeForUser, RedeemedCodes, Category, OfferDailyAnalytics
from .forms import OfferAdminForm, BrandAdminForm
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import format_html
import json

@admin.register(Brand)
class BrandAdmin(SummernoteModelAdmin):
    form = BrandAdminForm
    summernote_fields = ('description', 'about')
    list_display = ('slug', 'name', 'website')
    search_fields = ('name', 'website')
    list_per_page = 20

@admin.register(Offer)
class OfferAdmin(SummernoteModelAdmin):
    form = OfferAdminForm
    list_display = ('custom_id', 'brand', 'title', 'category', "sorting", "isExclusive")
    search_fields = ('brand', 'title')
    list_filter = ('category',)

@admin.register(OfferSEO)
class OfferSEOAdmin(admin.ModelAdmin):
    list_display = ('offer', 'title')
    search_fields = ('offer__name', 'title', 'keywords')
    list_per_page = 20

@admin.register(RedeemedCodes)
class RedeemedCodesAdmin(admin.ModelAdmin):
    list_display = ('offer_custom_id', 'codes_count', 'created_at', 'updated_at')
    search_fields = ('offer_custom_id',)
    list_per_page = 50
    readonly_fields = ("formatted_redeemed_codes_html",)

    def codes_count(self, obj):
        return len(obj.redeemed_codes)
    codes_count.short_description = "Total Codes"

    def formatted_redeemed_codes_html(self, obj):
        if not obj.redeemed_codes:
            return "-"

        rows = "".join(
            [f"<tr><td>{list(code.keys())[0]}</td><td>{list(code.values())[0]}</td></tr>" for code in obj.redeemed_codes]
        )
        table = f"""
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background:#000000; color:#fff; font-weight:bold;">
                <th style="width: 300px;">Redeemed Code</th>
                <th style="width: 250px;">Redeemed At (UTC)</th>
            </tr>
            {rows}
        </table>
        """
        return format_html(table)

    formatted_redeemed_codes_html.short_description = "Redeemed Codes Dashboard"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'title')
    search_fields = ('name', 'meta_keywords')
    list_per_page = 50

@admin.register(OfferDailyAnalytics)
class OfferDailyAnalyticsAdmin(admin.ModelAdmin):
    readonly_fields = ("formatted_offers_html",)

    def offers_count(self, obj):
        return len(obj.offers_data)
    offers_count.short_description = "Total Offers"

    def formatted_offers_html(self, obj):
        if not obj.offers_data:
            return "-"
        
        rows = "".join(
            [f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in obj.offers_data.items()]
        )
        table = f"""
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background:#000000; font-weight:bold;">
                <th style="width: 250px;">Offer</th>
                <th style="width: 30px;">Count</th>
            </tr>
            {rows}
        </table>
        """
        return format_html(table)

    formatted_offers_html.short_description = "Offers Data dashboard"
