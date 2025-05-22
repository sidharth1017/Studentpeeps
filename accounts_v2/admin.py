# admin.py
from django.contrib import admin
from .models import Register

class RegisterAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'phone', 'user_name')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_name(self, obj):
        return obj.user.first_name
    user_name.short_description = 'Name'

admin.site.register(Register, RegisterAdmin)
