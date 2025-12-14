from django.apps import AppConfig


class DemandForecastConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.demandforecast"

    def ready(self):
        # import here to avoid circular imports
        ...
