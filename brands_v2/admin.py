from django.contrib import admin
from .models import Brand, Offer, OfferSEO, OfferCodeForUser, RedeemedCodes
from .forms import OfferAdminForm, BrandAdminForm
from django_summernote.admin import SummernoteModelAdmin

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
    list_display = ('offer_custom_id', 'created_at', 'updated_at')
    search_fields = ('offer_custom_id',)
    list_per_page = 50
