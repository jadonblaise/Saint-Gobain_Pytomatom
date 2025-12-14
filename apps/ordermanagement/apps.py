from django.apps import AppConfig


class OrdermanagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ordermanagement"

    def ready(self):
        # import here to avoid circular imports
        ...
