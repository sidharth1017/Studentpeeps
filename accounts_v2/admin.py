from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Register


@admin.register(Register)
class RegisterAdmin(ModelAdmin):
    """People who signed up with email or phone OTP."""

    list_display = ("display_name", "user_email", "phone", "created_at")
    list_select_related = ("user",)
    search_fields = (
        "user__email",
        "user__username",
        "user__first_name",
        "user__last_name",
        "firstname",
        "lastname",
        "phone",
    )
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    fields = (
        "user",
        "phone",
        "firstname",
        "lastname",
        "gender",
        "birthday",
        "created_at",
    )

    @admin.display(description="Name")
    def display_name(self, obj):
        full_name = (obj.user.get_full_name() or "").strip()
        if full_name:
            return full_name
        profile_name = f"{obj.firstname} {obj.lastname}".strip()
        return profile_name or obj.user.username

    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email or ""
