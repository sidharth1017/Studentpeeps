from django.contrib import admin
from .models import Communication

# Register your models here.
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('channel', 'service')
admin.site.register(Communication, CommunicationAdmin)