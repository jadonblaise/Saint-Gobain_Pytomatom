from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.datetime.converters import datetimestring_to_datetime
from core.models.generics import StampedUUIDModel


def deactivate_old(qs: models.QuerySet) -> int:
    """
    Deactivate all objects in the queryset that are older than DATALAKE_DEACTIVATION_TIMEOUT (in hours).

    Should be called after all objects are imported (and transactions closed!) from the datalake.

    returns count of deactivated objects.
    """
    some_time_ago = timezone.now() - timedelta(hours=settings.DATALAKE_DEACTIVATION_TIMEOUT)
    return qs.filter(lastmodified_at__lt=some_time_ago).update(active=False)


class Plant(models.Model):
    division = models.CharField(max_length=50, unique=True)
    # Think about essential "Stammdaten" for a plant here..
    # name = models.CharField(max_length=50)
    # address = models.ForeignKey("Address", on_delete=models.CASCADE)

    def __str__(self) -> str:
        division = self.division
        return f"{division=}"


class SAPProduct(StampedUUIDModel):
    """
    A product is a product that is existing in SAP as a product.
    A sap product contains of

    """

    plant = models.ForeignKey("datalake.Plant", on_delete=models.CASCADE)

    sap_article_number = models.CharField(max_length=100, unique=True)

    ginger_code_17 = models.CharField(max_length=100, blank=True, default="")
    sap_technical_description = models.CharField(max_length=500, blank=True, default="")
    procurement_id = models.CharField(max_length=100, blank=True, default="")
    # Show customer the service level for a product:
    # CS= Cover Sheet, hat ein Deckblatt
    # MTS= Make to Stock, wird auf Lager produziert
    # MTO= Make to SAPOrder, wird auf Bestellung produziert
    # Out= Out of Service, Artikel service level ist nicht klassifiziert
    service_level = models.CharField(max_length=100, blank=True, default="")
    # deliverytime in days
    delivery_time = models.FloatField(null=True, default=None)
    # calculatory security stock, monitored to be able provide "make of stock"
    safety_stock = models.FloatField(null=True, default=None)
    safety_stock_unit = models.CharField(max_length=100, blank=True, default="")
    safety_stock_time = models.FloatField(null=True, default=None)
    safety_stock_internal_unit = models.CharField(max_length=100, blank=True, default="")
    safety_stock_quantity = models.FloatField(null=True)
    # product category for high value products (highly added value product)
    # HAVP = Highly Added Value Product
    # CLASSICS = Classics
    # AUTO = Automotive
    value_category = models.CharField(max_length=100, blank=True, default="")
    # emballage, verpackungsmaterial
    emballage = models.CharField(max_length=100, blank=True, default="")
    emballage_description = models.CharField(max_length=500, blank=True, default="")
    # libre commercial name
    commercial_name = models.CharField(max_length=100, blank=True, default="")
    family_description_long = models.CharField(max_length=500, blank=True, default="")
    family_description_short = models.CharField(max_length=100, blank=True, default="")
    family_description_code = models.CharField(max_length=100, blank=True, default="")
    family = models.CharField(max_length=100, blank=True, default="")
    sub_family = models.CharField(max_length=100, blank=True, default="")
    coating = models.CharField(max_length=100, blank=True, default="")
    impression = models.CharField(max_length=100, blank=True, default="")
    tint = models.CharField(max_length=100, blank=True, default="")
    quality = models.CharField(max_length=100, blank=True, default="")
    quality_name = models.CharField(max_length=100, blank=True, default="")
    # which treatment hd the glass, can be in alu ... etc
    treatment = models.CharField(max_length=100, blank=True, default="")
    # epasseure nominal, Glassdicke in mm, has leading zeros
    thickness = models.CharField(max_length=100, blank=True, default="")
    # dimension in mm x mm
    dimension = models.CharField(max_length=100, blank=True, default="")
    # dimension code - string like PLF, DLF, XXL ...
    dimension_description = models.CharField(max_length=100, blank=True, default="")
    # length in mm - five positions with leading zeros (e.g. 06000)
    length = models.CharField(max_length=100, blank=True, default="")
    # width in mm - five positions with leading zeros (e.g. 03210)
    width = models.CharField(max_length=100, blank=True, default="")
    # verpackungsart / package type
    package_type_code = models.CharField(max_length=100, blank=True, default="")
    # family for tonnage
    package_type_family = models.CharField(max_length=100, blank=True, default="")
    # alignment, orientation, direction / Ausrichtung des Glases im Paket
    orientation = models.CharField(max_length=100, blank=True, default="")
    error_marker = models.CharField(max_length=100, blank=True, default="")
    # zwischenglass pappe order papier
    inter_product_layer = models.CharField(max_length=100, blank=True, default="")
    # description intermediate layer (between glass discs) - string like LUC  # TBD: I think that means Lucite
    interleaf_description = models.CharField(max_length=500, blank=True, default="")
    # delivery time shown for customer
    lead_time_for_service = models.FloatField(null=True, default=None)
    # calculatory lead time
    lead_time = models.FloatField(null=True, default=None)
    pre_product_length = models.FloatField(null=True, default=None)
    pre_product_width = models.FloatField(null=True, default=None)
    count_of_glass_in_package = models.PositiveIntegerField(null=True, default=None)

    def lstrip_sap_material_number(self) -> str:
        """get SAP article number (sap_article_number) without leading zeros ('0000123' -> '123')"""
        return self.sap_article_number.lstrip("0")

    def __str__(self) -> str:
        plant = self.plant
        sap_article_number = self.sap_article_number
        return f"SAPProduct object: {plant=} | {sap_article_number=}"


class GlassPane(StampedUUIDModel):
    """
    A GlassPane on stock
        glass plate
        or
        sheet
    is one 'disc' of glass (Blatt, Scheibe) in a rack
    can be identified by its "GBS" (Glas-Begleit-Schein) -> sheet_id
    """

    plant = models.ForeignKey("datalake.Plant", on_delete=models.CASCADE)
    # We have to soft-delete old entries, if they are not updated by an API request occassionally.
    active = models.BooleanField(default=True)
    # A sheet is one 'disc' of glass (Blatt, Scheibe) in a rack
    sheet_id = models.CharField(max_length=100, unique=True)
    position_on_rack = models.IntegerField(null=True, default=None)
    # 'Lagernde Menge'. But what means that (count of available panes)?
    nb_volumes = models.IntegerField(null=True, default=None)

    sap_material = models.CharField(max_length=100, blank=True, default="")
    sap_order_no = models.CharField(max_length=100, blank=True, default="")
    sap_technical_description = models.CharField(max_length=500, blank=True, default="")
    quality = models.CharField(max_length=20, blank=True, default="")
    previous_quality_code = models.CharField(max_length=100, blank=True, default="")
    # emballage, verpackungsmaterial
    emballage = models.CharField(max_length=100, blank=True, default="")
    # verpackungsart / package type
    package_type_code = models.CharField(max_length=100, blank=True, default="")
    # dimension code - string like PLF, DLF, XXL ...
    dimension_description = models.CharField(max_length=100, blank=True, default="")
    # length in mm - five positions with leading zeros (e.g. 06000)
    length = models.CharField(max_length=100, blank=True, default="")
    # width in mm - five positions with leading zeros (e.g. 03210)
    width = models.CharField(max_length=100, blank=True, default="")
    # which treatment hd the glass, can be in alu ... etc
    treatment = models.CharField(max_length=100, blank=True, default="")
    # epasseure nominal, Glassdicke in mm, has leading zeros
    thickness = models.CharField(max_length=100, blank=True, default="")
    production_start_date = models.CharField(max_length=100, blank=True, default="")
    production_end_date = models.CharField(max_length=100, blank=True, default="")
    glass_age = models.PositiveIntegerField(null=True, default=None)
    age_date = models.CharField(max_length=100, blank=True, default="")
    wh_location_name = models.CharField(max_length=100, blank=True, default="")
    production_line = models.CharField(max_length=100, blank=True, default="")
    interleaf_description = models.CharField(max_length=500, blank=True, default="")
    primary_pack_material_id = models.CharField(max_length=100, blank=True, default="")
    primary_stillage_desc = models.CharField(max_length=100, blank=True, default="")
    secondary_stillage_desc = models.CharField(max_length=200, blank=True, default="")
    sqm = models.DecimalField(null=True, default=None, max_digits=12, decimal_places=3)
    tons = models.DecimalField(null=True, default=None, max_digits=12, decimal_places=3)
    cover_sheet_id = models.CharField(max_length=100, blank=True, default="")
    quality_status = models.CharField(max_length=100, blank=True, default="")
    reason_code = models.CharField(max_length=100, blank=True, default="")
    quality_comment_obs = models.TextField(blank=True, default="")
    quality_comment_remarks = models.TextField(blank=True, default="")
    stacker = models.CharField(max_length=100, blank=True, default="")  # (Stapler)

    total_tons_on_stock: Decimal  # just for type hinting, will be used in views and subqueries

    def __str__(self) -> str:
        plant = self.plant
        sheet_id = self.sheet_id
        sap_material = self.sap_material
        return f"Stock (sheet) object: {plant=} | {sheet_id=} | {sap_material=}"

    def get_production_start_date(self) -> datetime | None:
        return datetimestring_to_datetime(datetimestring=self.production_start_date, format="%Y-%m-%d %H:%M:%S")

    def get_production_end_date(self) -> datetime | None:
        return datetimestring_to_datetime(datetimestring=self.production_end_date, format="%Y-%m-%d %H:%M:%S")


class Purchase(StampedUUIDModel):
    plant = models.ForeignKey("datalake.Plant", on_delete=models.CASCADE)
    purchase_order_no = models.CharField(max_length=100)
    ginger_code_17 = models.CharField(max_length=100)
    sales_order_no = models.CharField(max_length=100, blank=True, default="")
    supplier_name = models.CharField(max_length=100, blank=True, default="")
    delivery_should_be_done = models.CharField(max_length=100, blank=True, default="")
    sap_material = models.CharField(max_length=100, blank=True, default="")
    sap_technical_description = models.CharField(max_length=500, blank=True, default="")
    # verpackungsart / package type
    package_type_code = models.CharField(max_length=100, blank=True, default="")
    coating = models.CharField(max_length=100, blank=True, default="")
    # epasseure nominal, Glassdicke in mm, has leading zeros
    thickness = models.CharField(max_length=100, blank=True, default="")
    # length in mm - five positions with leading zeros (e.g. 06000)
    length = models.CharField(max_length=100, blank=True, default="")
    # width in mm - five positions with leading zeros (e.g. 03210)
    width = models.CharField(max_length=100, blank=True, default="")
    quality = models.CharField(max_length=100, blank=True, default="")
    order_quantity_volumes = models.FloatField(null=True, default=None)
    order_quantity_tons = models.FloatField(null=True, default=None)
    order_quantity_qm = models.FloatField(null=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["purchase_order_no", "ginger_code_17"], name="unique_order_numbers_purchase"
            ),
        ]

    def __str__(self) -> str:
        plant = self.plant
        purchase_order_no = self.purchase_order_no
        ginger_code_17 = self.ginger_code_17
        sap_material = self.sap_material
        return f"Purchase object: {plant=} | {purchase_order_no=} | {ginger_code_17=} | {sap_material=}"

    def lstrip_sap_material_number(self) -> str:
        """get SAP article number (sap_article_number) without leading zeros ('0000123' -> '123')"""
        return self.sap_material.lstrip("0")


class SAPOrder(StampedUUIDModel):
    """
    SAP orders are the 'order management' orders provided by SAP via the datalake endpoint.
    """

    plant = models.ForeignKey("datalake.Plant", on_delete=models.CASCADE)
    # We have to soft-delete old entries, if they are not updated by an API request occassionally.
    active = models.BooleanField(default=True)
    sales_order = models.CharField(max_length=100)
    ginger_code_17 = models.CharField(max_length=100)
    expected_loading_date = models.CharField(max_length=100, blank=True, default="")
    ship_to_customer = models.CharField(max_length=100, blank=True, default="")
    customer_name = models.CharField(max_length=100, blank=True, default="")
    country_code = models.CharField(max_length=100, blank=True, default="")
    entry_date = models.CharField(max_length=100, blank=True, default="")
    delivery_note = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(max_length=100, blank=True, default="")
    reservation_project_name = models.CharField(max_length=100, blank=True, default="")
    sap_material = models.CharField(max_length=100, blank=True, default="")
    position = models.CharField(max_length=100, blank=True, default="")
    order_quantity = models.FloatField(null=True, default=None)
    net_volumes_sqm = models.FloatField(null=True, default=None)
    net_weight_to = models.FloatField(null=True, default=None)
    sub_family = models.CharField(max_length=100, blank=True, default="")
    coating = models.CharField(max_length=100, blank=True, default="")
    tint = models.CharField(max_length=100, blank=True, default="")
    # dimension code - string like PLF, DLF, XXL ...
    dimension_description = models.CharField(max_length=100, blank=True, default="")
    classification_lamination = models.CharField(max_length=100, blank=True, default="")
    quality = models.CharField(max_length=100, blank=True, default="")
    # which treatment hd the glass, can be in alu ... etc
    treatment = models.CharField(max_length=100, blank=True, default="")
    # epasseure nominal, Glassdicke in mm, has leading zeros
    thickness = models.CharField(max_length=100, blank=True, default="")
    # family for tonnage
    package_type_family = models.CharField(max_length=100, blank=True, default="")
    production_planning_class = models.CharField(max_length=100, blank=True, default="")
    # length in mm - five positions with leading zeros (e.g. 06000)
    length = models.CharField(max_length=100, blank=True, default="")
    # width in mm - five positions with leading zeros (e.g. 03210)
    width = models.CharField(max_length=100, blank=True, default="")
    stock_place = models.CharField(max_length=100, blank=True, default="")
    # verpackungsart / package type
    package_type_code = models.CharField(max_length=100, blank=True, default="")
    error_marker = models.CharField(max_length=100, blank=True, default="")
    # zwischenglass pappe order papier
    inter_product_layer = models.CharField(max_length=100, blank=True, default="")
    # description intermediate layer (between glass plates) - string like LUC  # TBD: I think that means Lucite
    interleaf_description = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sales_order", "ginger_code_17"],
                name="unique_order_numbers_order_management",
            ),
        ]

    def __str__(self) -> str:
        plant = self.plant
        sales_order = self.sales_order
        ginger_code_17 = self.ginger_code_17
        sap_material = self.sap_material
        return f"SAPOrder object: {plant=} | {sales_order=} | {ginger_code_17=} | {sap_material=}"

    def lstrip_sap_material_number(self) -> str:
        """get SAP article number (sap_article_number) without leading zeros ('0000123' -> '123')"""
        return self.sap_material.lstrip("0")

    def lstrip_sales_order(self) -> str:
        return self.sales_order.lstrip("0")

    def get_expected_loading_datetime(self) -> datetime | None:
        return datetimestring_to_datetime(datetimestring=self.expected_loading_date, format="%Y-%m-%d %H:%M:%S")
