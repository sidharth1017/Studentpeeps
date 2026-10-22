from django.apps import AppConfig


class UtilitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilities'

    def ready(self):
        from utilities.logging.config import configure_logging
        from utilities.logging.hooks import install_requests_logging_hook

        configure_logging()
        install_requests_logging_hook()
