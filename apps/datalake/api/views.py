import json
import logging
from pathlib import Path

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from django.conf import settings
from django.db.utils import DataError
from django.http import JsonResponse
from django.utils import timezone

from apps.authentication.api.backends import JWTAuthentication
from apps.datalake.imports import (
    DataValidationError,
    update_or_create_order_management,
    update_or_create_pane,
    update_or_create_product,
    update_or_create_purchase,
)
from core.inout.files import write_to_disk
from core.models.fields import add_user_now_fields

from ..models import GlassPane, SAPOrder, SAPProduct, deactivate_old


log = logging.getLogger("django.datalake")


class ImportSAPProductsView(APIView):
    """
    Import products from a list of products provided via json.

    * Requires token authentication.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # default permission is "is authenticated"

    def get(self, request, format=None):
        return JsonResponse(
            {"message": "Method not allowed. POST a list of products in request body instead."},
            status=405,
        )
    
    def post(self, request, format=None):
        """
        Process a list of products provided in the request body.
        """
        content = json.loads(request.body)

        dump_payload(content=content, name="sap-products")

        try:
            products = content["products"]
        except KeyError:
            return JsonResponse(
                {"message": "Key Missing. Please provide a list of 'products' in the request body"}, status=400
            )
        for product in products:
            try:
                update_or_create_product(product | add_user_now_fields(request))
            except DataValidationError as e:
                log.warning(f"SAPPRODUCTS 400 {str(e)}")
                return JsonResponse({"message": str(e)}, status=400)
            except DataError as e:
                log.warning(f"SAPPRODUCTS 400 {str(e)}")
                return JsonResponse({"message": str(e)}, status=400)
        message = f"{len(products)} products imported successfully"
        log.info(f"SAPPRODUCTS 201 {message}")
        return JsonResponse({"message": message}, status=201)


class ImportStocksView(APIView):
    """
    Import stocks from a list of stocks provided via json.

    * Requires token authentication.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # default permission is "is authenticated"

    def get(self, request, format=None):
        return JsonResponse(
            {"message": "Method not allowed. POST a list of stocks in request body instead."},
            status=405,
        )

    def post(self, request, format=None):
        """
        Process a list of stocks provided in the request body.
        """
        content = json.loads(request.body)

        dump_payload(content=content, name="stocks")

        try:
            stocks = content["stocks"]
        except KeyError:
            return JsonResponse(
                {"message": "Key Missing. Please provide a list of 'stocks' in the request body"}, status=400
            )
        for stock in stocks:
            try:
                update_or_create_pane(stock | add_user_now_fields(request))
            except DataValidationError as e:
                log.warning(f"STOCKS 400 {str(e)}")
                return JsonResponse({"message": str(e)}, status=400)
            except DataError as e:
                log.warning(f"STOCKS 400 {str(e)}")
                return JsonResponse({"message": str(e)}, status=400)
        message = f"{len(stocks)} stocks imported successfully"
        log.info(f"STOCKS 201 {message}")

        # Deactivate old.
        active_stock = GlassPane.objects.filter(active=True)
        deactivated = deactivate_old(active_stock)
        log.info(f"STOCKS {deactivated=}")

        return JsonResponse({"message": message}, status=201)


class ImportPurchasesView(APIView):
    """
    Import purchases from a list of purchases provided via json.

    * Requires token authentication.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # default permission is "is authenticated"

    def get(self, request, format=None):
        return JsonResponse(
            {"message": "Method not allowed. POST a list of purchases in request body instead."},
            status=405,
        )

    def post(self, request, format=None):
        """
        Process a list of purchases provided in the request body.
        """
        content = json.loads(request.body)

        dump_payload(content=content, name="purchases")

        try:
            purchases = content["purchases"]
        except KeyError:
            return JsonResponse(
                {"message": "Key Missing. Please provide a list of 'purchases' in the request body"}, status=400
            )
        for purchase in purchases:
            try:
                update_or_create_purchase(purchase | add_user_now_fields(request))
            except DataValidationError as e:
                log.warning(f"PURCHASES 400 {str(e)}")
                return JsonResponse({"message": str(e)}, status=400)
            except DataError as e:
                log.warning(f"PURCHASES 400 {str(e)}")
                return JsonResponse({"message": str(e)}, status=400)
        message = f"{len(purchases)} purchases imported successfully"
        log.info(f"PURCHASES 201 {message}")
        return JsonResponse({"message": message}, status=201)


class ImportOrdersView(APIView):
    """
    Import orderManagements from a list of orders provided via json.

    * Requires token authentication.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # default permission is "is authenticated"

    def get(self, request, format=None):
        return JsonResponse(
            {"message": "Method not allowed. POST a list of orders in request body instead."},
            status=405,
        )

    def post(self, request, format=None):
        """
        Process a list of orders provided in the request body.
        """
        content = json.loads(request.body)

        dump_payload(content=content, name="orders")

        try:
            orders = content["orders"]
        except KeyError:
            return JsonResponse(
                {"message": "Key Missing. Please provide a list of 'orders' in the request body"}, status=400
            )
        for order in orders:
            try:
                update_or_create_order_management(order | add_user_now_fields(request))
            except DataValidationError as e:
                log.warning(f"ORDERS 400 {str(e)}")
                return JsonResponse({"message": str(e)}, status=400)
            except DataError as e:
                log.warning(f"ORDERS 400 {str(e)}")
                return JsonResponse({"message": str(e)}, status=400)
        message = f"{len(orders)} orders imported successfully."
        log.info(f"ORDERS 201 {message}")

        # Deactivate old.
        active_orders = SAPOrder.objects.filter(active=True)
        deactivated = deactivate_old(active_orders)
        log.info(f"ORDERS {deactivated=}")

        return JsonResponse({"message": message}, status=201)


class ProtectionTestView(APIView):
    """
    ... example view that requires authentication.

    * Requires token authentication.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # default permission is "is authenticated"

    def get(self, request, format=None):
        """
        Return a list of all planets.
        """
        planets = ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune"]
        return JsonResponse({"planets": planets})


def dump_payload(content, name: str):
    """Temporary Workaround - Save request content from datalake as file."""
    try:
        # todo: delete old files as first step to avoid low memory space.
        temp = Path(settings.ROOT_DIR) / "temp"
        temp.mkdir(exist_ok=True, parents=True)
        parsed_content = str(content)
        write_to_disk(
            path=temp / f"datalake-content-{name}-{timezone.now().isoformat().replace(':', '_')}.txt",
            content=parsed_content,
        )
    except Exception:
        # We do not want to handle any exception here because this would block the main business logic.
        pass
