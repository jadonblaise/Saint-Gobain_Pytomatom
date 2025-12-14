import io

import pandas as pd

from django.conf import settings

from apps.resources import read, export

from . import transformations, cessions_modification


FILENAME_SAP_EXPORT = "sap-upload.xlsx"
FILENAME_DEMAND_FORECAST_EXPORT = "demand-forecast.xlsx"


def demand_forecast_automation(
    *,
    reference_data_buffer: io.BytesIO | None = None,
    lg_codes_buffer: io.BytesIO | None = None,
    dach_forecast_buffer: io.BytesIO | None = None,
    microstrategy_buffer: io.BytesIO | None = None,
    shipping_plants_buffer: io.BytesIO | None = None,
    cessions_buffer: io.BytesIO | None = None,
    output_as_sap_upload: bool = False,
) -> io.BytesIO:
    """
    Main function for Demand Forecast using only the bytesIO buffers.
    """

    lg_codes = (
        # table with lg_codes to reduce dach_forecast
        # ! currently second row is used as header - this is a potential bug risk
        read.as_df(
            path=settings.RESOURCES_DIR / "demand-forecast" / "G035G048 production LG Codes.xlsx",
            sheet_name="Production",
            divergent_header=1,
        )
        if not lg_codes_buffer
        else read.as_df(buffer=lg_codes_buffer, sheet_name="Production", divergent_header=1)
    )

    # Stammdaten
    reference_data = (
        read.as_df(
            path=settings.RESOURCES_DIR / "reference-data" / "MSTR_DATA_COUNTRY_GERMANY_Planner 2023.xlsx",
            sheet_name="Products",
        )
        if not reference_data_buffer
        else read.as_df(buffer=reference_data_buffer, sheet_name="Products")
    )

    dach_forecast = (
        read.as_df(path=settings.RESOURCES_DIR / "demand-forecast" / "DACH_Forecast.csv", as_csv=True, seperator="\t")
        if not dach_forecast_buffer
        else read.as_df(buffer=dach_forecast_buffer, as_csv=True, seperator="\t")
    )

    microstrategy = (
        read.as_df(
            path=settings.RESOURCES_DIR / "demand-forecast" / "MSTR_DATA_COUNTRY_GERMANY_Planner.xlsx",
            sheet_name="Sales",
        )
        if not microstrategy_buffer
        else read.as_df(buffer=microstrategy_buffer, sheet_name="Sales")
    )

    shipping_plants = (
        read.as_df(
            path=settings.RESOURCES_DIR / "demand-forecast" / "Shipping Plant Split.xlsx",
            sheet_name="DEMAND Plant Split",
        )
        if not shipping_plants_buffer
        else read.as_df(buffer=shipping_plants_buffer, sheet_name="DEMAND Plant Split")
    )

    cessions = (
        read.as_df(
            path=settings.RESOURCES_DIR / "demand-forecast" / "cession-costumers.xlsx",
            sheet_name="Cessions",
        )
        if not cessions_buffer
        else read.as_df(buffer=cessions_buffer, sheet_name="Cessions")
    )

    forecast = forecast_demand(
        reference_data=reference_data,
        lg_codes=lg_codes,
        dach_forecast=dach_forecast,
        microstrategy=microstrategy,
        shipping_plants=shipping_plants,
        cessions=cessions,
        output_as_sap_upload=output_as_sap_upload,
    )

    filename: str = FILENAME_DEMAND_FORECAST_EXPORT if not output_as_sap_upload else FILENAME_SAP_EXPORT

    buffered = export.to_xlsx(df=forecast, filename=filename, buffer=True, sheet_name="DemandForecast")

    return buffered


def forecast_demand(
    *,
    reference_data: pd.DataFrame,
    lg_codes: pd.DataFrame,
    dach_forecast: pd.DataFrame,
    microstrategy: pd.DataFrame,
    shipping_plants: pd.DataFrame,
    cessions: pd.DataFrame,
    output_as_sap_upload: bool,
) -> pd.DataFrame:
    """
    Main function for automated demand forecast,
    expects all data prepared as df and returns the prediction df
    """

    dach_forecast = transformations.reduce_dach_forecast(forecast=dach_forecast, lg_codes=lg_codes)
    dach_forecast = transformations.clean_dach_forecast(forecast=dach_forecast)
    microstrategy = transformations.clean_microstrategy_forecast(forecast=microstrategy)
    shipping_plants = transformations.clean_shipping_plants(df=shipping_plants)

    forecast = transformations.merge_dach_microstrategy_forecast(
        dach_forecast=dach_forecast, microstrategy_forecast=microstrategy
    )
    forecast = transformations.merge_shipping_plants(forecast=forecast, shipping_plants=shipping_plants)

    if output_as_sap_upload:
        forecast = transformations.transform_forecast_to_sap_upload(forecast=forecast, reference_data=reference_data)

    forecast, _, _, _ = cessions_modification.modification_through_cessions(
        demand_forecast_df=forecast, cessions_df=cessions
    )

    return forecast
