from django.urls import path

from . import views
from . import views_download  # added by blaise to test the orderbook logic without Celery

app_name = "ordermanagement"

urlpatterns = [
    path("ordermanagement/download/", views.DownloadOrderManagementView.as_view(), name="download"),
    path("api/ordermanagement.json", views.OrdermanagementApiView.as_view(), name="api"),
    path("ordermanagement/", views.OrdermanagementIndexView.as_view(), name="index"),
    path("ordermanagement/download-quick/", views_download.DownloadOrderManagementQuickView.as_view(), name="download-quick"),  # added by blaise to test the orderbook logic without Celery
]
