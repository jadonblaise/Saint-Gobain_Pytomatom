import io

from django.views import View

from core.inout import download

from .forecast import demand_forecast_automation, FILENAME_SAP_EXPORT, FILENAME_DEMAND_FORECAST_EXPORT


class DownloadDemandForecastView(View):
    def post(self, request):
        # Get the form data

        # TBD: reference_data included sheet 'Sales' which is content of microstrategy
        # (but table design is not exact the same)
        # think about to merge both in one - later with connection via API

        output_as_sap_upload: bool = "as_sap_upload" in request.POST.getlist("divergence")
        reference_data_buffer: io.BytesIO | None = request.FILES.get("reference_data")
        lg_codes_buffer: io.BytesIO | None = request.FILES.get("lg_codes")
        dach_forecast_buffer: io.BytesIO | None = request.FILES.get("dach_forecast")
        microstrategy_buffer: io.BytesIO | None = request.FILES.get("microstrategy")
        shipping_plants_buffer: io.BytesIO | None = request.FILES.get("shipping_plants")
        cessions_buffer: io.BytesIO | None = request.FILES.get("cessions")

        forecast_buffer = demand_forecast_automation(
            reference_data_buffer=reference_data_buffer,
            lg_codes_buffer=lg_codes_buffer,
            dach_forecast_buffer=dach_forecast_buffer,
            microstrategy_buffer=microstrategy_buffer,
            shipping_plants_buffer=shipping_plants_buffer,
            output_as_sap_upload=output_as_sap_upload,
            cessions_buffer=cessions_buffer,
        )

        # Return the file as a downloadable attachment
        filename = FILENAME_DEMAND_FORECAST_EXPORT if not output_as_sap_upload else FILENAME_SAP_EXPORT
        return download.excel_response(buffer=forecast_buffer, filename=filename)
