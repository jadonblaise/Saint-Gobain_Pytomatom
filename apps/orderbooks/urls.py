from django.urls import path

from . import views


app_name = "orderbooks"

urlpatterns = [path("download/", views.DownloadOrderManagementView.as_view(), name="automation-download")]
