from django.urls import path

from . import views


app_name = "automation"

urlpatterns = [path("", views.VueAutomationFrontendInDjangoView.as_view(), name="frontend")]
