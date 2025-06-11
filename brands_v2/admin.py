from django.contrib import admin
from .models import BrandOnboard, ExclusiveOffer, NonExclusiveOffer, Seo

# Register your models here.
class BrandOnboardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
admin.site.register(BrandOnboard, BrandOnboardAdmin)

class ExclusiveOfferAdmin(admin.ModelAdmin):
    list_display = ('brand', 'title')
admin.site.register(ExclusiveOffer, ExclusiveOfferAdmin)

admin.site.register(NonExclusiveOffer)
admin.site.register(Seo)
