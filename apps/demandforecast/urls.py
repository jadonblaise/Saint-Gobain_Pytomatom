from django.urls import path

from . import views


app_name = "demandforecast"

urlpatterns = [path("download/", views.DownloadDemandForecastView.as_view(), name="automation-download")]
