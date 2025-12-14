from django.apps import AppConfig


class OrderbookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orderbooks"

    def ready(self):
        # import here to avoid circular imports
        ...
