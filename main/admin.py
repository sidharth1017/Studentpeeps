import django.contrib.auth.admin  # noqa: F401  registers User and Group before we replace them
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django_summernote.admin import SummernoteModelAdminMixin
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import (
    Contact,
    Foundation,
    Subscribe,
    Homepage,
    PolicyPage,
    PromoStripBanner,
    HomepageSection,
    HomepageFeaturedSku,
)


# Register your models here.

class ContactAdmin(ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    readonly_fields = ('created_at',)
admin.site.register(Contact, ContactAdmin)

class FoundationAdmin(ModelAdmin):
    list_display = ('name','collegename','email', 'coursename')
# admin.site.register(Foundation, FoundationAdmin)
# admin.site.register(Resource)
class SubscribeAdmin(ModelAdmin):
    list_display = ("email",)
    search_fields = ("email",)

admin.site.register(Subscribe, SubscribeAdmin)


class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    ordering = ['-date_joined']
    list_display = ('username', 'email', 'first_name', 'is_staff', 'date_joined')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

class HomepageAdmin(ModelAdmin):
    list_display = ('layout_type', 'position', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('layout_type',)
    ordering = ('position',)
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Homepage, HomepageAdmin)

class PolicyPageAdmin(SummernoteModelAdminMixin, ModelAdmin):
    summernote_fields = ('content',)
    list_display = ('title', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('title', 'slug')
admin.site.register(PolicyPage, PolicyPageAdmin)


@admin.register(PromoStripBanner)
class PromoStripBannerAdmin(ModelAdmin):
    list_display = (
        "name",
        "is_enabled",
        "priority",
        "starts_at",
        "ends_at",
        "updated_at",
    )
    list_filter = ("is_enabled",)
    search_fields = ("name", "message", "cta_label")
    fieldsets = (
        (None, {"fields": ("name", "is_enabled", "priority")}),
        ("Copy & link", {"fields": ("message", "cta_label", "cta_href")}),
        (
            "Colours",
            {"fields": ("background_color", "text_color", "cta_color")},
        ),
        (
            "Schedule",
            {
                "fields": ("starts_at", "ends_at"),
                "description": "Leave both empty to show whenever the banner is enabled (no end date).",
            },
        ),
    )


class HomepageFeaturedSkuInline(TabularInline):
    model = HomepageFeaturedSku
    extra = 1
    fields = (
        "sort_order",
        "sku",
        "display_name",
        "subtitle",
        "is_enabled",
        "starts_at",
        "ends_at",
    )
    ordering = ("sort_order", "id")


@admin.register(HomepageSection)
class HomepageSectionAdmin(ModelAdmin):
    list_display = ("section_key", "is_enabled", "starts_at", "ends_at", "updated_at")
    list_filter = ("is_enabled", "section_key")
    search_fields = ("section_key", "title")
    inlines = (HomepageFeaturedSkuInline,)
    fieldsets = (
        (None, {"fields": ("section_key", "is_enabled")}),
        ("Copy", {"fields": ("title", "subtitle", "cta_label", "cta_href")}),
        (
            "Schedule",
            {
                "fields": ("starts_at", "ends_at"),
                "description": "Leave both empty to keep the section live until you disable it.",
            },
        ),
    )


@admin.register(HomepageFeaturedSku)
class HomepageFeaturedSkuAdmin(ModelAdmin):
    list_display = ("section", "sort_order", "sku", "display_name", "is_enabled", "starts_at", "ends_at")
    list_filter = ("section", "is_enabled")
    search_fields = ("sku", "display_name", "subtitle")
    ordering = ("section", "sort_order", "id")
    autocomplete_fields = ("section",)
