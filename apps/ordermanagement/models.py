import logging
from collections import OrderedDict
from datetime import datetime

import pandas as pd

from django.db import models
from django.db.models.query import QuerySet

from core.models.converters import model_to_dict
from core.models.generics import IndexedTimeStampedModel, UserStampedModel, UUIDModel


log = logging.getLogger("django.ordermanagement")


class OrderBookEntry(IndexedTimeStampedModel, UserStampedModel):
    """
    This model represents a single entry in the orderbook.
    """

    order = models.ForeignKey("datalake.SAPOrder", on_delete=models.CASCADE, related_name="orderbooks")

    class OtifPredictor(models.TextChoices):
        OK = "OK"
        NP = "NP"
        NOK = "NOK"

    sap_material = models.CharField(max_length=100, blank=True, default="")
    sap_order_creation_date = models.CharField(max_length=100, blank=True, default="")

    expected_loading_week = models.IntegerField(blank=True, null=True)
    expected_loading_date = models.DateField(blank=True, null=True)

    expected_loading_date_daybefore = models.DateField(blank=True, null=True)  # past information.

    net_volumes_sqm = models.FloatField(blank=True, null=True)
    net_weight_to = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)  # (amount of panes)

    volume_daybefore = models.FloatField(blank=True, null=True)  # past information.

    coating = models.CharField(max_length=100, blank=True, default="")
    tint = models.CharField(max_length=100, blank=True, default="")
    thickness = models.CharField(max_length=100, blank=True, default="")

    sales_order = models.CharField(max_length=100, blank=True, default="")
    ship_to_customer = models.CharField(max_length=100, blank=True, default="")
    ship_to_customer_name = models.CharField(max_length=100, blank=True, default="")
    ship_to_country = models.CharField(max_length=100, blank=True, default="")

    delivery_note = models.CharField(max_length=100, blank=True, default="")
    order_status = models.CharField(max_length=100, blank=True, default="")
    sub_family = models.CharField(max_length=100, blank=True, default="")
    treatment = models.CharField(max_length=100, blank=True, default="")

    reservation_project_name = models.CharField(max_length=100, blank=True, default="")
    quality = models.CharField(max_length=100, blank=True, default="")
    length = models.CharField(max_length=100, blank=True, default="")
    width = models.CharField(max_length=100, blank=True, default="")

    package_type_code = models.CharField(max_length=100, blank=True, default="")
    package_type_family = models.CharField(max_length=100, blank=True, default="")
    production_planning_class = models.CharField(max_length=100, blank=True, default="")
    dimension_description = models.CharField(max_length=100, blank=True, default="")

    planned_production_date = models.DateField(blank=True, null=True, default=None)
    planned_production_week = models.IntegerField(blank=True, null=True, default=None)

    ob_uid = models.CharField(max_length=100, primary_key=True, unique=True)

    otif_predictor = models.CharField(max_length=3, choices=OtifPredictor.choices, default=OtifPredictor.NOK)

    planner_status = models.CharField(max_length=100, blank=True, default="")
    planner_comment = models.CharField(max_length=100, blank=True, default="")
    planner_new_production_calender_week = models.CharField(max_length=100, blank=True, default="")
    planner_estimation_or_task = models.CharField(max_length=100, blank=True, default="")

    laminate = models.CharField(max_length=100, blank=True, default="")

    ginger_code = models.CharField(max_length=100, blank=True, default="")

    stock_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.otif_predictor} {self.ginger_code} {self.sap_material} {self.expected_loading_date}"

    def get_sap_material(self) -> str:
        """get SAP article number (sap_article_number) without leading zeros ('0000123' -> '123')"""
        return self.sap_material.lstrip("0")

    def translate_attr(self, attr: str) -> str:
        return self.column_translation().get(attr, attr)

    @classmethod
    def translate_country(cls, country_code: str) -> str:
        return cls.country_codes().get(country_code, country_code)

    @classmethod
    def convert_string_to_integer(cls, value: str) -> int:
        return int(value) if isinstance(value, str) and value.isdigit() else -1

    @classmethod
    def columns(cls) -> tuple:
        return tuple(cls.column_translation().values())

    @classmethod
    def fields(cls) -> tuple:
        return tuple(cls.column_translation().keys())

    @classmethod
    def column_translation(cls) -> OrderedDict[str, str]:
        """
        Will determine the xlsx header-names.
        """
        return OrderedDict(
            {
                "expected_loading_week": "KW",
                "ginger_code": "Ginger Code 17",
                "expected_loading_date": "Sales Expected Loading Date",
                # "expected_loading_date_daybefore": "Expected Loading Date - day before",
                "ship_to_customer_name": "ShipTo Customer",
                "ship_to_country": "ShipTo Country",
                "sap_order_creation_date": "Order Creation Date",
                "sales_order": "Sales Order",
                "delivery_note": "Delivery Note",
                "order_status": "Sales Order Status",
                "sub_family": "Sub-Family",
                "reservation_project_name": "Resa Project Name",
                "coating": "Coating",
                "tint": "Tint",
                "thickness": "Nominal Thickness",
                "dimension_description": "Size",
                "laminate": "Laminate",
                "quality": "Quality",
                "treatment": "Surface Protection",
                "package_type_code": "Packaging",
                "package_type_family": "Pack Type",
                "production_planning_class": "Class",
                "length": "Length",
                "width": "Width",
                "sap_material": "Material Plant",
                "volume": "VOL",
                "volume_daybefore": "VOL - day before",
                "net_volumes_sqm": "M2",
                "net_weight_to": "TO",
                "pk": "ob_UID",
                "planner_status": "Status",
                "planner_estimation_or_task": "ETD",
                "planner_comment": "Comment",
                "planner_new_production_calender_week": "NP CW",
                "created_at": "hidden_created_at",
                "lastmodified_at": "hidden_lastmodified_at",
                # ...
                "stock_count": "Stock count",
                "otif_predictor": "OTIF Predictor",
                "planned_production_date": "Planned production date",
                "planned_production_week": "Planned production week",
            }
        )

    @classmethod
    def country_codes(cls) -> dict:
        return {
            "AT": "Austria",
            "BE": "Belgium",
            "BG": "Bulgaria",
            "CH": "Switzerland",
            "CZ": "Czech Republic",
            "DE": "Germany",
            "DK": "Denmark",
            "EE": "Estonia",
            "ES": "Spain",
            "FI": "Finland",
            "FR": "France",
            "GB": "United Kingdom",
            "GR": "Greece",
            "HR": "Croatia",
            "HU": "Hungary",
            "IE": "Ireland",
            "IT": "Italy",
            "LT": "Lithuania",
            "LU": "Luxembourg",
            "LV": "Latvia",
            "NL": "Netherlands",
            "NO": "Norway",
            "PL": "Poland",
            "PT": "Portugal",
            "RO": "Romania",
            "SE": "Sweden",
            "SI": "Slovenia",
            "SK": "Slovakia",
            "US": "United States",
            "JP": "Japan",
            "IS": "Iceland",
            "IL": "IL (unknown)",
            "AE": "United Arab Emirates",
        }


def to_exportable_dataframe(orderbook: QuerySet[OrderBookEntry]) -> pd.DataFrame:
    """
    Converts a QuerySet of OrderBookEntries to an exportable pandas.DataFrame.
    (should be convertible to a xlsx response already..)
    """
    translation: dict = OrderBookEntry.column_translation()

    orderentries = [
        {
            # Get rid of dt fields.
            translation.get(column, column): value if type(value) is not datetime else value.strftime("%Y-%m-%d")
            for column, value in model_to_dict(
                order,
                fields=OrderBookEntry.fields(),
                preserve_editable=True,
                preserve_primary_key=True,
            ).items()
            if translation.get(column, column) in OrderBookEntry.columns()
        }
        for order in orderbook.all()
    ]

    # Add entries.
    df = pd.DataFrame.from_records(orderentries)

    # Format nominal thickness (e.g. "0490" -> "4,9")
    thickness_col = translation.get("thickness", "Nominal Thickness")
    if thickness_col in df.columns:
        def _fmt_thickness(val):
            if isinstance(val, str) and val.isnumeric():
                return str(int(val) / 100).replace(".", ",")
            return val
        df[thickness_col] = df[thickness_col].apply(_fmt_thickness)

    # Convert 'Stock count' from Decimal into Float type...
    try:
        df["Stock count"] = df["Stock count"].astype(float)
    except ValueError as exc:
        log.error(f"Cannot parse 'Stock count' column into Float type. {exc=}")
        raise exc  # ! force application abort to avoid shifting the failure.

    # Reorder columns.
    try:
        df = df[list(OrderBookEntry.columns())]
    except KeyError as e:
        log.warning(f"Could not reorder columns: {e}. Probably empty dataframe.")
        df = pd.DataFrame(columns=OrderBookEntry.columns())

    # Translate country codes.
    ship_to_country_naming = OrderBookEntry.column_translation().get("ship_to_country", "ship_to_country")
    df[ship_to_country_naming] = df[ship_to_country_naming].apply(
        lambda code: OrderBookEntry.translate_country(country_code=code)
    )
    # Workaround: convert glass panes' length and width into INT type
    width_naming = OrderBookEntry.column_translation().get("width", "width")
    length_naming = OrderBookEntry.column_translation().get("length", "length")
    df[width_naming] = df[width_naming].apply(lambda width: OrderBookEntry.convert_string_to_integer(value=width))
    df[length_naming] = df[length_naming].apply(lambda length: OrderBookEntry.convert_string_to_integer(value=length))
    
    # Sort by Sub-Family, tint and coating alphabetically ascending
    sub_family_col = translation.get("sub_family", "Sub-Family")
    tint_col = translation.get("tint", "Tint")
    coating_col = translation.get("coating", "Coating")
    if sub_family_col in df.columns and not df.empty:
        df = df.sort_values(by=[sub_family_col, tint_col, coating_col], ascending=True)
        df = df.reset_index(drop=True)  # Reset index after sorting

    return df


class DayBeforeComparison_LastInsert(UUIDModel, IndexedTimeStampedModel):
    """# ToDo:____"""

    insert_date = models.DateField("Last Insert Date", auto_now=True, unique=True)


class DayBeforeComparison_NeededInformation(UUIDModel, IndexedTimeStampedModel):
    """# ToDo:____"""

    active = models.BooleanField()
    last_insert = models.ForeignKey(DayBeforeComparison_LastInsert, on_delete=models.CASCADE)
    ob_uid = models.CharField(max_length=100)
    volume = models.FloatField(blank=True, null=True)
    expected_loading_date = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('last_insert', 'ob_uid',)
