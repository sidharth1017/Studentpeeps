from django.contrib import admin
from .models import Communication, OTPSendLog, GiftCardSettings, PaymentMethodOption

# Register your models here.
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('channel', 'service')
admin.site.register(Communication, CommunicationAdmin)

class OTPSendLogAdmin(admin.ModelAdmin):
    list_display = ('phone', 'count', 'date')
admin.site.register(OTPSendLog, OTPSendLogAdmin)


@admin.register(GiftCardSettings)
class GiftCardSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'purchases_enabled', 'updated_at')
    list_editable = ('purchases_enabled',)
    fieldsets = (
        (None, {
            'fields': ('purchases_enabled', 'hold_message'),
            'description': (
                'OFF = customers can still pay, but nothing is sent to Woohoo. '
                'Paid orders are put on hold and the customer sees the message below.'
            ),
        }),
    )

    def has_add_permission(self, request):
        return not GiftCardSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        GiftCardSettings.load()  # make sure the row exists so it shows up in the list
        return super().changelist_view(request, extra_context)


@admin.register(PaymentMethodOption)
class PaymentMethodOptionAdmin(admin.ModelAdmin):
    list_display = ('display_label', 'method', 'enabled', 'sort_order', 'fee_percent', 'discount_percent', 'description')
    list_editable = ('enabled', 'sort_order', 'fee_percent', 'discount_percent', 'description')
    list_display_links = ('display_label',)
    ordering = ('sort_order', 'id')
    fields = ('method', 'enabled', 'sort_order', 'label', 'description', 'fee_percent', 'discount_percent')

    def get_readonly_fields(self, request, obj=None):
        return ('method',) if obj else ()

    def has_add_permission(self, request):
        return False  # rows are created automatically, one per supported method

    def has_delete_permission(self, request, obj=None):
        return False  # untick "enabled" to hide a method instead

    def changelist_view(self, request, extra_context=None):
        PaymentMethodOption.ensure_defaults()
        return super().changelist_view(request, extra_context)

