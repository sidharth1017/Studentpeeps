from django.contrib import admin
from .models import RequestBrand, Contact, Foundation, Resource, Brand, Subscribe, Homepage, PolicyPage
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_summernote.admin import SummernoteModelAdmin


# Register your models here.

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    readonly_fields = ('created_at',)
admin.site.register(Contact, ContactAdmin)

# admin.site.register(RequestBrand)
class FoundationAdmin(admin.ModelAdmin):
    list_display = ('name','collegename','email', 'coursename')
# admin.site.register(Foundation, FoundationAdmin)
# admin.site.register(Resource)
# admin.site.register(Brand)
admin.site.register(Subscribe)


class CustomUserAdmin(BaseUserAdmin):
    ordering = ['-date_joined']  # Sort by newest
    list_display = ('username', 'email', 'first_name', 'is_staff', 'date_joined')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class HomepageAdmin(admin.ModelAdmin):
    list_display = ('layout_type', 'position', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('layout_type',)
    ordering = ('position',)
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Homepage, HomepageAdmin)

class PolicyPageAdmin(SummernoteModelAdmin):
    summernote_fields = ('content')
    list_display = ('title', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('title', 'slug')
admin.site.register(PolicyPage, PolicyPageAdmin)
