# -- Modular settings ---------------------------------------------------------
# These settings are imported in the __init__.py of the base directory explicitly.
# To add a new setting, also edit the __init__.py
# -----------------------------------------------------------------------------

# APPS definition
# -----------------------------------------------------------------------------
# ! order is important
# project specific apps
CORE_APPS: list[str] = [
    "core.app.CoreConfig",
    # To replace with a the custom userapp -> comment "core.users" out & comment in
    # apps.users.apps.UsersConfig in LOCAL_APPS
    # "core.users",
]
PROJECT_APPS: list[str] = [
    "apps.automation.apps.AutomationConfig",
    "apps.orderbooks.apps.OrderbookConfig",
    "apps.demandforecast.apps.DemandForecastConfig",
    "apps.datalake.apps.DatalakeConfig",
    "apps.ordermanagement.apps.OrdermanagementConfig",
    "apps.sharepoint.apps.SharepointConfig",
]
# custom apps for all projects
LOCAL_APPS: list[str] = [
    # custom apps
    "apps.users.apps.UsersConfig",
]
DJANGO_APPS: list[str] = [
    # default django-apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS: list[str] = [
    "crispy_forms",
    "crispy_tailwind",
    "django_extensions",
    "widget_tweaks",
    # "rest_framework",
    "django_celery_beat",
    "django_celery_results",
    "corsheaders",
]
# See: https://docs.djangoproject.com/en/4.1/ref/settings/#installed-apps
# local apps shall override djangos default, so order is important
INSTALLED_APPS = CORE_APPS + PROJECT_APPS + LOCAL_APPS + DJANGO_APPS + THIRD_PARTY_APPS
