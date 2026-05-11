from django.apps import AppConfig


class GiftcardConfig(AppConfig):
    name = 'giftcard'

    def ready(self):
        from . import signals
