# admin.py
from django.contrib import admin
<<<<<<< Updated upstream
from .models import Register, UnVerified, AbandonedSignup
=======
from .models import Register, UnVerified
>>>>>>> Stashed changes

class RegisterAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'phone', 'created_at')
    readonly_fields = ('created_at',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_name(self, obj):
        return obj.user.first_name
    user_name.short_description = 'First Name'

admin.site.register(Register, RegisterAdmin)

admin.site.register(UnVerified)
<<<<<<< Updated upstream
admin.site.register(AbandonedSignup)
=======
>>>>>>> Stashed changes
