# admin.py
from django.contrib import admin
from .models import Register, UnVerified, AbandonedSignup, UnVerifiedIdUpload

class RegisterAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'phone', 'created_at', 'is_verified')
    readonly_fields = ('created_at',)
    list_filter = ('is_verified',)  # <-- Add this line for filtering by is_verified

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_name(self, obj):
        return obj.user.first_name
    user_name.short_description = 'First Name'

admin.site.register(Register, RegisterAdmin)

admin.site.register(UnVerified)
admin.site.register(UnVerifiedIdUpload)
admin.site.register(AbandonedSignup)
