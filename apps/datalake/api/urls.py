from django.urls import path

from . import views


app_name = "datalake"


urlpatterns = [
    path("protectiontest/", views.ProtectionTestView.as_view(), name="test-protected"),  # type: ignore
    path("import/products/", views.ImportSAPProductsView.as_view(), name="import-products"),  # type: ignore
    path("import/stocks/", views.ImportStocksView.as_view(), name="import-stocks"),  # type: ignore
    path("import/purchases/", views.ImportPurchasesView.as_view(), name="import-purchases"),  # type: ignore
    path("import/orders/", views.ImportOrdersView.as_view(), name="import-orders"),  # type: ignore
]
