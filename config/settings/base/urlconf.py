# -- Modular settings ---------------------------------------------------------
# These settings are imported in the __init__.py of the base directory explicitly.
# To add a new setting, also edit the __init__.py
# -----------------------------------------------------------------------------

# Django Admin URL.
# a little protection to script-kiddie-attacks. This is no REAL security.
ADMIN_URL = "hidden-admin-pytomatom"

# https://docs.djangoproject.com/en/4.1/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "api:api-root"
LOGOUT_REDIRECT_URL = "api:api-root"
# LOGIN_REDIRECT_URL = "/"
# https://docs.djangoproject.com/en/4.1/ref/settings/#login-url
LOGIN_URL = "api:api-root"  # "users:login"

ROOT_URLCONF = "config.urls.routes"
API_BASE_URL: str = "api"
