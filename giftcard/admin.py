from django.contrib import admin
from .models import Provider, ProviderCategory, CategoryMapping, ProviderAuthToken, ProviderApiLog, ProviderProduct, ProductOverride
# Register your models here.

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('id', 'name')
    list_per_page = 20

@admin.register(ProviderCategory)
class ProviderCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'provider', 'provider_category_id')
    search_fields = ('id', 'name', 'provider_category_id')
    list_per_page = 20

@admin.register(CategoryMapping)
class CategoryMappingAdmin(admin.ModelAdmin):
    list_display = ('platform_category', 'provider_category', 'is_primary')
    search_fields = ('platform_category__name', 'provider_category__name')

@admin.register(ProviderAuthToken)
class ProviderAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('provider', 'token_type', 'expires_at', 'is_active')
    search_fields = ('provider__name',)

@admin.register(ProviderApiLog)
class ProviderApiLogAdmin(admin.ModelAdmin):
    list_display = ('provider', 'method', 'url', 'response_status', 'created_at')
    search_fields = ('provider__name',)

@admin.register(ProviderProduct)
class ProviderProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'provider')
    search_fields = ('provider__name', 'sku', 'name')

@admin.register(ProductOverride)
class ProductOverrideAdmin(admin.ModelAdmin):
    list_display = ('product', 'category', 'name')
    search_fields = ('product__provider__name', 'product__sku', 'name')