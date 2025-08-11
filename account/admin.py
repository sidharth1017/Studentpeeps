from django.contrib import admin

from account.models import College
from .models import *
# Register your models here.
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name','emails', 'created_at')
admin.site.register(College, CollegeAdmin)

# class RegisterAdmin(admin.ModelAdmin):
#     list_display = ('firstname','gender', 'email' ,'institution', 'institution_email')
# admin.site.register(Registers, RegisterAdmin)
# class UploadAdmin(admin.ModelAdmin):
#     list_display = ('username','firstname','lastname', 'email')
# admin.site.register(Upload, UploadAdmin)
# class UnVerifiedAdmin(admin.ModelAdmin):
#     list_display = ('username','firstname', 'email' ,'institution', 'institution_email')
# admin.site.register(UnVerified, UnVerifiedAdmin)
# admin.site.register(Signup)
# class YourdetailAdmin(admin.ModelAdmin):
#     list_display = ('firstname','lastname', 'gender')
# admin.site.register(Yourdetail, YourdetailAdmin)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'payment_status')


# admin.site.register(Payment, PaymentAdmin)
