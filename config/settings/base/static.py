# -- Modular settings ---------------------------------------------------------
# These settings are imported in the __init__.py of the base directory explicitly.
# To add a new setting, also edit the __init__.py
# -----------------------------------------------------------------------------
from importlib import import_module
from types import ModuleType

from . import paths

vite: ModuleType | None
try:
    vite = import_module("config.settings.base.thirdparty.vite")
except ImportError:
    vite = None

# STATIC files (CSS, JavaScript, Images)
# -----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/4.1/howto/static-files/
# STATIC_ROOT = str((paths.ROOT_DIR / "assets").resolve())
STATIC_ROOT = str(paths.ROOT_DIR / "staticfiles")
# To use a CDN (e.g.: for whitenoise), SET a statichost, (preferably as env):
STATIC_HOST = ""
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = f"{STATIC_HOST}/assets/"
# https://docs.djangoproject.com/en/4.1/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(paths.ROOT_DIR / "assets")]
# See: https://docs.djangoproject.com/en/4.1/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "config.finders.AssetsAppDirectoriesFinder",
]
# PM R.S. übernimmt die Verantwortung für MEDIA_STORAGE auf der internen Platte [[2023-08-23]] in prod.
# MEDIA_ROOT = str((paths.ROOT_DIR / "media").resolve())
MEDIA_ROOT = str(paths.ROOT_DIR / "media")

SHAREPOINT_MEDIA = paths.ROOT_DIR / "media" / "sharepoint"
SHAREPOINT_MEDIA.mkdir(exist_ok=True)

MEDIA_URL = f"{STATIC_HOST}/media/"

USE_VITE_ASSETS = False

if vite is not None:
    if USE_VITE_ASSETS:
        STATICFILES_DIRS += [f"{vite.DJANGO_VITE_ASSETS_PATH}"]
    if vite.DJANGO_VITE_DEV_MODE:
        STATICFILES_FINDERS += ["config.settings.base.thirdparty.vite.ViteFrontendFinder"]
