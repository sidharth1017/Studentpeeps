from django.contrib import admin
from .models import Provider, ProviderCategory, CategoryMapping, ProviderAuthToken, ProviderApiLog, ProviderProduct, ProductOverride, Cart, Order, PaymentTransaction
# Register your models here.

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'user', 'session_key', 'is_active', 'created_at')
    search_fields = ('cart_id', 'user__username', 'session_key')
    list_filter = ('is_active', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('reference_id', 'user', 'total_amount', 'status', 'payment_gateway', 'customer_email', 'created_at')
    search_fields = ('reference_id', 'user__username', 'customer_email', 'gateway_order_id', 'gateway_payment_id', 'woohoo_order_id')
    list_filter   = ('status', 'payment_gateway', 'created_at')
    readonly_fields = ('items_snapshot', 'woohoo_response', 'gateway_order_id', 'gateway_payment_id', 'woohoo_order_id')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display  = ('order', 'gateway', 'gateway_order_id', 'gateway_payment_id', 'amount', 'status', 'created_at')
    search_fields = ('order__reference_id', 'gateway_order_id', 'gateway_payment_id')
    list_filter   = ('gateway', 'status', 'created_at')
    readonly_fields = ('raw_response',)

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