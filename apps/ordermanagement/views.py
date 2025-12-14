import io
from datetime import timedelta

import httpx
import pandas as pd

from django.conf import settings
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.datalake.info import get_last_datalake_update_date
from apps.datalake.models import Plant
from apps.excelstyler.exceptions import ExcelSheetNotFound
from apps.sharepoint.access import rewrite_latest_orderbook_from_and_to_sharepoint
from core.inout import download, files
from core.views.mixins import CacheMixin

from .exceptions import PlantDoesNotExist
from .logic import manage_orders
from .models import OrderBookEntry, to_exportable_dataframe
from .porz_style import styling_of_excel_sheet


def generate_order_management_buffer(plant_ids):
    orderbook: QuerySet[OrderBookEntry] = manage_orders(plant_ids=plant_ids)  # type: ignore[annotation-unchecked]

    one_month_ago = timezone.now() - timedelta(days=30)
    df: pd.DataFrame = to_exportable_dataframe(orderbook.filter(lastmodified_at__gte=one_month_ago))  # type: ignore[annotation-unchecked]

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, sheet_name=settings.OM_SHEET_NAME, index=False)

    buffer = styling_of_excel_sheet(buffer=buffer, sheet_name=settings.OM_SHEET_NAME)
    buffer.seek(0)
    return buffer


def get_plant_ids(divisions: list):
    """
    Select Plants.
    """
    plant_ids = []
    for plant in divisions:
        try:
            plant_id = Plant.objects.get(division=plant).id  # type: ignore
        except Plant.DoesNotExist:
            raise PlantDoesNotExist(f"Plant '{plant}' does not exist in the database.")
        plant_ids.append(plant_id)
    return plant_ids


@method_decorator(csrf_exempt, name="dispatch")
class DownloadOrderManagementView(View):
    def post(self, request):
        today: str = timezone.localtime().date().strftime("%Y-%m-%d")  # type: ignore[annotation-unchecked]

        # divisions = [p.division for p in request.user.plants.all()]
        # plant_ids = [p.id for p in request.user.plants.all()]
        try:
            plant_ids = get_plant_ids(divisions=["G035"])
        except PlantDoesNotExist as e:
            return JsonResponse({"message": e}, status=404)

        if not plant_ids:
            return JsonResponse(
                {"message": f"No Plant tied to user '{request.user=}' in the database."},
                status=404,
            )

        # HACK: manually add everything on button klick to the sharepoint as well.. (to integrate feedback on click)
        try:
            spf = rewrite_latest_orderbook_from_and_to_sharepoint(division="G035")
        except ExcelSheetNotFound as e:
            return JsonResponse({"message": f"Could not style workbook {e}"}, status=501)
        except httpx.RequestError as exc:
            return JsonResponse({"message": f"An error occurred while requesting {exc.request.url!r}."}, status=424)
        except httpx.HTTPStatusError as exc:
            return JsonResponse(
                {"message": f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."},
                status=exc.response.status_code,
            )

        name = str(spf.file).lstrip("sharepoint/")
        content: bytes = files.read_from_disk(
            path=settings.SHAREPOINT_MEDIA / name, mode="rb"
        )  # type: ignore[assignment]
        buffer = io.BytesIO(content)

        return download.excel_response(
            buffer=buffer, filename=f"{settings.PROJECT_TITLE}-{settings.OM_SHEET_NAME.lower()}-{today}.xlsx"
        )


class OrdermanagementIndexView(CacheMixin, TemplateView):
    template_name = "ordermanagement/frontend.html.djt"
    cache_timeout = 1  # 60 * 2  # seconds

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_datalake_update"] = get_last_datalake_update_date()
        return context


class OrdermanagementApiView(View):
    def get(self, request):
        if not request.headers.get("Authorization") == settings.EXTERNAL_OM_API_ACCESS_TOKEN:
            return JsonResponse({"message": "Not authorized"}, status=401)

        try:
            plant_ids = get_plant_ids(divisions=settings.EXTERNAL_OM_API_DIVISIONS)
        except PlantDoesNotExist as e:
            return JsonResponse({"message": e}, status=404)

        if not plant_ids:
            return JsonResponse(
                {"message": f"No Plant tied to user '{request.user=}' in the database."},
                status=404,
            )

        try:
            orderbook: QuerySet[OrderBookEntry] = manage_orders(plant_ids=plant_ids)  # type: ignore[annotation-unchecked]
        except httpx.RequestError as exc:
            return JsonResponse({"message": f"An error occurred while requesting {exc.request.url!r}."}, status=424)
        except httpx.HTTPStatusError as exc:
            return JsonResponse(
                {"message": f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."},
                status=exc.response.status_code,
            )

        one_month_ago = timezone.now() - timedelta(days=30)
        serializable = [model_to_dict(ob) for ob in list(orderbook.filter(lastmodified_at__gte=one_month_ago))]
        return JsonResponse({"orderbook": serializable}, status=200)
