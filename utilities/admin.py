from django.contrib import admin
from .models import Communication, OTPSendLog

# Register your models here.
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('channel', 'service')
admin.site.register(Communication, CommunicationAdmin)

class OTPSendLogAdmin(admin.ModelAdmin):
    list_display = ('phone', 'count', 'date')
admin.site.register(OTPSendLog, OTPSendLogAdmin)