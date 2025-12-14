from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.conf import settings
from django.urls import (
    include,
    path,
)
from django.views.generic import RedirectView


app_name = "api"


@api_view(["GET"])
@authentication_classes(())
@permission_classes((AllowAny,))
def api_root(request, format=None):
    """Root response answering with system status and version."""
    return Response({"status": "up and running", "version": settings.VERSION})


urlpatterns = [
    # default apis, should not be removed
    path("", api_root),
    # JWT-authentication
    path("", include("apps.authentication.api.urls")),
    # this is a fix for the namespace "api:api-root", that got polluted
    # by the custom apps and has to go last
    path("", RedirectView.as_view(url=""), name="api-root"),
]

if settings.DEBUG:
    # development only
    pass
