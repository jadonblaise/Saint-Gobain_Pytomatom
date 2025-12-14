import io

from django.views import View

from core.inout import download

from .atom import order_management_automation


class DownloadOrderManagementView(View):
    def post(self, request):
        # Get the form data
        new_orders_buffer: io.BytesIO | None = request.FILES.get("new_orders")
        old_orders_buffer: io.BytesIO | None = request.FILES.get("old_orders")
        orion_raw_buffer: io.BytesIO | None = request.FILES.get("orion_raw")
        article_ginger_buffer: io.BytesIO | None = request.FILES.get("article_ginger")
        float_plan_buffer: io.BytesIO | None = request.FILES.get("float_plan")
        coater_plan_buffer: io.BytesIO | None = request.FILES.get("coater_plan")

        om_buffer = order_management_automation(
            new_orders_buffer=new_orders_buffer,
            old_orders_buffer=old_orders_buffer,
            orion_raw_buffer=orion_raw_buffer,
            article_ginger_buffer=article_ginger_buffer,
            float_plan_buffer=float_plan_buffer,
            coater_plan_buffer=coater_plan_buffer,
        )

        # Return the file as a downloadable attachment
        return download.excel_response(buffer=om_buffer, filename="output.xlsx")
