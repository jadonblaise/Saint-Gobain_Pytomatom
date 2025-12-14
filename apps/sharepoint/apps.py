from django.apps import AppConfig


class SharepointConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sharepoint"

    def ready(self):
        # import here to avoid circular imports
        ...
