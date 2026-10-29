from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from django.utils.html import format_html

from .models import (
    Provider,
    ProviderCategory,
    CategoryMapping,
    ProviderAuthToken,
    ProviderApiLog,
    ProviderProduct,
    ProductOverride,
    Cart,
    Order,
    PaymentTransaction,
)

# Register your models here.


def _brand_logo_preview(file_field):
    if file_field:
        return format_html(
            '<img src="{}" alt="" style="max-height:72px;max-width:160px;object-fit:contain;" />',
            file_field.url,
        )
    return "—"


class ProductOverrideInline(StackedInline):
    model = ProductOverride
    can_delete = False
    extra = 0
    max_num = 1
    readonly_fields = ("brand_logo_preview", "logo_dev_etag", "logo_fetched_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "category",
                    "name",
                    "margin",
                    "status",
                    "status_reason",
                    "brand_name",
                    "brand_code",
                    "brand_logo_preview",
                    "brand_logo",
                    "logo_domain",
                    "logo_dev_etag",
                    "logo_fetched_at",
                    "thumbnail",
                ),
            },
        ),
    )

    @admin.display(description="Current brand logo")
    def brand_logo_preview(self, obj):
        return _brand_logo_preview(obj.brand_logo)

@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('cart_id', 'user', 'session_key', 'is_active', 'created_at')
    search_fields = ('cart_id', 'user__username', 'session_key')
    list_filter = ('is_active', 'created_at')

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display  = ('reference_id', 'user', 'total_amount', 'status', 'payment_gateway', 'customer_email', 'created_at')
    search_fields = ('reference_id', 'user__username', 'customer_email', 'gateway_order_id', 'gateway_payment_id', 'woohoo_order_id')
    list_filter   = ('status', 'payment_gateway', 'created_at')
    readonly_fields = ('items_snapshot', 'woohoo_response', 'gateway_order_id', 'gateway_payment_id', 'woohoo_order_id')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(ModelAdmin):
    list_display  = ('order', 'gateway', 'gateway_order_id', 'gateway_payment_id', 'amount', 'status', 'created_at')
    search_fields = ('order__reference_id', 'gateway_order_id', 'gateway_payment_id')
    list_filter   = ('gateway', 'status', 'created_at')
    readonly_fields = ('raw_response',)

@admin.register(Provider)
class ProviderAdmin(ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('id', 'name')
    list_per_page = 20

@admin.register(ProviderCategory)
class ProviderCategoryAdmin(ModelAdmin):
    list_display = ('id', 'name', 'provider', 'provider_category_id')
    search_fields = ('id', 'name', 'provider_category_id')
    list_per_page = 20

@admin.register(CategoryMapping)
class CategoryMappingAdmin(ModelAdmin):
    list_display = ('platform_category', 'provider_category', 'is_primary')
    search_fields = ('platform_category__name', 'provider_category__name')

@admin.register(ProviderAuthToken)
class ProviderAuthTokenAdmin(ModelAdmin):
    list_display = ('provider', 'token_type', 'expires_at', 'is_active')
    search_fields = ('provider__name',)

@admin.register(ProviderApiLog)
class ProviderApiLogAdmin(ModelAdmin):
    list_display = ('provider', 'method', 'url', 'response_status', 'created_at')
    search_fields = ('provider__name',)

@admin.register(ProviderProduct)
class ProviderProductAdmin(ModelAdmin):
    list_display = ("name", "sku", "provider", "override_logo_status")
    search_fields = ("provider__name", "sku", "name", "brand_name")
    inlines = (ProductOverrideInline,)

    @admin.display(description="Override logo")
    def override_logo_status(self, obj):
        try:
            override = obj.override
        except ProductOverride.DoesNotExist:
            return "No override"
        if override.brand_logo:
            return format_html(
                '<img src="{}" style="height:28px;max-width:80px;object-fit:contain;" />',
                override.brand_logo.url,
            )
        return "Override exists, no logo file"

@admin.register(ProductOverride)
class ProductOverrideAdmin(ModelAdmin):
    list_display = (
        "product",
        "category",
        "name",
        "status",
        "margin",
        "logo_fetched_at",
        "brand_logo_preview",
    )
    list_filter = ("status",)
    search_fields = ("product__provider__name", "product__sku", "name", "brand_name", "logo_domain")
    readonly_fields = ("brand_logo_preview", "logo_dev_etag", "logo_fetched_at")
    fieldsets = (
        (None, {
            'fields': (
                'product',
                'category',
                'name',
                'description',
                'tnc_content',
                'margin',
                'status',
                'status_reason',
            ),
        }),
        ('Brand', {
            'fields': (
                'brand_name',
                'brand_code',
                'brand_logo_preview',
                'brand_logo',
                'logo_domain',
                'logo_dev_etag',
                'logo_fetched_at',
            ),
        }),
        ('Media overrides', {
            'fields': ('thumbnail',),
        }),
    )

    @admin.display(description="Preview")
    def brand_logo_preview(self, obj):
        return _brand_logo_preview(obj.brand_logo)