from django.apps import AppConfig


class DatalakeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.datalake"

    def ready(self):
        # import here to avoid circular imports
        ...
