import datetime
import logging
from datetime import date
from decimal import Decimal
from typing import NamedTuple

from django.conf import settings
from django.db.models import Case, CharField, Value, When
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.utils import timezone

from apps.datalake.models import GlassPane, SAPOrder, SAPProduct
from apps.ordermanagement.plans import coater, floater
from core.conversions import to_decimal
from core.datetime.converters import calender_week

from .exceptions import InvalidOrderException
from .models import DayBeforeComparison_LastInsert, DayBeforeComparison_NeededInformation, OrderBookEntry


log = logging.getLogger("django.ordermanagement")


class Orderbook(NamedTuple):
    entries: list[OrderBookEntry]
    stock: dict[str, Decimal]
    production_planner_coat: dict
    production_planner_float: dict


def stock_per_material(panes: QuerySet[GlassPane]) -> dict[str, Decimal]:
    """
    Calculate the available stock per ginger_code on annotated glasspanes.
    """
    # naive implementation
    stock = {}
    for pane in panes:
        ginger_code = pane.ginger_code  # type: ignore # glasspanes are annotated with ginger_code
        if ginger_code is None:
            log.debug(f"{pane.pk=} has no ginger_code.")
            continue
        if ginger_code not in stock:
            stock[ginger_code] = Decimal(0)
        if pane.tons is not None:
            stock[ginger_code] += pane.tons
        log.debug(
            f"{pane.pk=} with {pane.sheet_id=} has {ginger_code=} and {pane.tons=}. Current {stock[ginger_code]=}"
        )
    stock = {k: v.quantize(settings.STOCK_DECIMAL_PLACES) for k, v in stock.items()}

    # hint: debugging - seems to be okay.
    log.debug(f"{stock=}")
    return stock


def insert_and_store_needed_info(orderbook: Orderbook) -> Orderbook:
    """
    Store current needed information for future comparison and include past information into Orderbook.
    """
    # --- check last date in DB and create new one if necessary. ---
    current_date = datetime.datetime.now().date()
    # get last set insert in DB:
    last_inserts = DayBeforeComparison_LastInsert.objects.all().order_by("-insert_date")

    if last_inserts.count() == 0:
        # no last insert (DB table is empty):
        new_last_insert = DayBeforeComparison_LastInsert.objects.create()
        store_info_for_future(orderbook=orderbook, last_insert=new_last_insert)
        save_last_insert_obj(last_insert=new_last_insert)

    elif last_inserts.count() == 1:

        last_insert: DayBeforeComparison_LastInsert = last_inserts[0]  # first

        if last_insert.insert_date == current_date:
            # this insert is today:
            store_info_for_future(orderbook=orderbook, last_insert=last_insert)
            save_last_insert_obj(last_insert=last_insert)

        elif last_insert.insert_date < current_date:
            # this insert is from past:
            new_last_insert = DayBeforeComparison_LastInsert.objects.create()
            orderbook = include_past_info_into_orderbook(last_insert=last_insert, orderbook=orderbook)
            store_info_for_future(orderbook=orderbook, last_insert=new_last_insert)
            save_last_insert_obj(last_insert=new_last_insert)

    elif last_inserts.count() > 1:

        last_insert: DayBeforeComparison_LastInsert = last_inserts[0]  # first
        last_last_insert: DayBeforeComparison_LastInsert = last_inserts[1]  # second from django.conf import settings

        if last_insert.insert_date == current_date and last_last_insert.insert_date < current_date:
            # last insert is today and last last insert is from past:
            orderbook = include_past_info_into_orderbook(last_insert=last_last_insert, orderbook=orderbook)
            store_info_for_future(orderbook=orderbook, last_insert=last_insert)
            save_last_insert_obj(last_insert=last_insert)

        elif last_insert.insert_date < current_date:
            # last insert is from past:
            new_last_insert = DayBeforeComparison_LastInsert.objects.create()
            orderbook = include_past_info_into_orderbook(last_insert=last_insert, orderbook=orderbook)
            store_info_for_future(orderbook=orderbook, last_insert=new_last_insert)
            save_last_insert_obj(last_insert=new_last_insert)
            
    return orderbook


def save_last_insert_obj(last_insert: DayBeforeComparison_LastInsert):
    last_insert.save()  # date will be set automatically.
    log.debug(f"Save current day: {last_insert=}")


def include_past_info_into_orderbook(last_insert: DayBeforeComparison_LastInsert, orderbook: Orderbook) -> Orderbook:
    """
    Get past information and include in current orderbook.
    """
    for entry in orderbook.entries:

        # get storred info of entry:
        try:
            storred_info_of_entry = DayBeforeComparison_NeededInformation.objects.get(
                ob_uid=entry.ob_uid,
                last_insert=last_insert,
            )
        except Exception as exc:
            log.debug((f"{exc=} {entry.ob_uid=}"))
            continue

        # add past information:
        entry.volume_daybefore = storred_info_of_entry.volume
        entry.expected_loading_date_daybefore = storred_info_of_entry.expected_loading_date
    
    return orderbook


def store_info_for_future(orderbook: Orderbook, last_insert: DayBeforeComparison_LastInsert):
    """
    Store current information (today) to use in future.
    """
    for entry in orderbook.entries:

        ob_uid = entry.ob_uid
        volume = entry.volume
        expected_loading_date = entry.expected_loading_date

        if ob_uid is None or ob_uid == "":
            log.warning(f"'ob_uid' in Orderbook entry is not present. {ob_uid=} {volume=} {expected_loading_date=}")
            continue

        # update last one or insert new info to DB:
        try:
            obj = DayBeforeComparison_NeededInformation.objects.get(last_insert=last_insert, ob_uid=ob_uid)
            obj.active = True
            obj.volume = volume
            obj.expected_loading_date = expected_loading_date
            obj.save()
        except DayBeforeComparison_NeededInformation.DoesNotExist as exc:
            log.debug(f"{exc=}")
            DayBeforeComparison_NeededInformation.objects.create(
                last_insert=last_insert,
                ob_uid=ob_uid,
                active=True,
                volume=volume,
                expected_loading_date=expected_loading_date,
            )

        log.debug(f"Save information of current day: {last_insert=} {ob_uid=} {volume=} {expected_loading_date=}")


def manage_orders(plant_ids: list[str]) -> QuerySet[OrderBookEntry]:
    """
    Create the orderbook queryset
    """

    # Directly import planners from SharePoint here to integrate the most recent feedback.
    # Could also trigger the celery-task .
    from apps.sharepoint import access  # ! hint: hide for tests/debugging.

    # today = date.today()
    # from apps.sharepoint import tasks
    # tasks.get_porz_plannings.apply_async()
    access.import_porz_plans_from_sharepoint()  # ! hint: hide for tests/debugging.
    
    # todo: outsource two lines above to a flow-step before to avoid touching code for tests. 

    # Get all relevant orders for the given plant. (active, in the plant)
    all_orders = list(
        SAPOrder.objects.filter(plant__pk__in=plant_ids, active=True).order_by(
            # tbd: first part should be 'ginger_code_17'
            "ginger_code_17",
            "expected_loading_date",
            # "sales_order",
            # "thickness",
        )
    )

    considered_sap_orders = all_orders
    # queryset = GlassPane.objects.all()
    # Filter for the latest (active) glasspanes only.
    # queryset = GlassPane.objects.filter(plant__pk__in=plant_ids, active=True)
    queryset = GlassPane.objects.filter(active=True, quality_status="RAS")
    # Annotate all the corresponding glasspanes with the ginger_code for each.
    panes = annotate_glasspanes_with_ginger_code(panes=queryset, plant_ids=plant_ids)

    # Legacy: Annotate all the corresponding glasspanes with the total tons on stock for each.
    # panes = annotate_glasspanes_with_total_tons(panes=queryset, plant_ids=plant_ids)

    available_stock = stock_per_material(panes=panes)

    # Create the orderbook.
    orderbook = Orderbook(
        entries=[],
        stock=available_stock,
        production_planner_coat=coater.get_coater_plan(),
        production_planner_float=floater.get_float_plan(),
    )
    for order in considered_sap_orders:
        try:
            orderbook = add_entry_manipulate_stock(order_id=str(order.pk), orderbook=orderbook)
        except InvalidOrderException as exc:
            log.warning(f"{exc=}")
            continue

    insert_and_store_needed_info(orderbook=orderbook)

    processed = []
    for entry in orderbook.entries:
        entry_dict = model_to_dict(entry)

        order = SAPOrder.objects.get(pk=entry.order.pk)
        ob_uid = entry_dict.pop("ob_uid")
        entry_dict.pop("order")

        # Load old entries to fetch 'old' needed information.
        try:
            entry_old = OrderBookEntry.objects.get(pk=ob_uid)

            # fetch Planner Feedback and insert them into new entry
            entry_dict["planner_comment"] = entry_old.planner_comment
            entry_dict["planner_status"] = entry_old.planner_status
            entry_dict["planner_estimation_or_task"] = entry_old.planner_estimation_or_task
            entry_dict["planner_new_production_calender_week"] = entry_old.planner_new_production_calender_week

        except OrderBookEntry.DoesNotExist:
            # No old entry found, creating new later.
            pass

        # Line added by blaise to fix the issue with the update_or_create method.
        # Django 4.x compatible version (without create_defaults)
        # Prepare defaults - DON'T include ob_uid in defaults
        entry_dict["order"] = order

        # update_or_create will use ob_uid for lookup, and update/create with entry_dict
        instance, created = OrderBookEntry.objects.update_or_create(
            ob_uid=ob_uid,  # Lookup key
            defaults=entry_dict  # Fields to update/create (already has 'order' now)
        )

        if created:
            log.debug(f"OrderBookEntry: {instance.pk=} created.")
        else:
            log.debug(f"OrderBookEntry: {instance.pk=} updated.")

        processed.append(instance.pk)

    return OrderBookEntry.objects.filter(pk__in=processed).order_by(
        "ginger_code",
        "expected_loading_date",
    )


def transfer_order_to_order_book_entry(*, order_id: str) -> OrderBookEntry:
    order = SAPOrder.objects.get(pk=order_id)
    expected_loading_dt = order.get_expected_loading_datetime()
    net_volumes_sqm = order.net_volumes_sqm
    net_weight_to = order.net_weight_to
    expected_loading_date = expected_loading_dt.date() if expected_loading_dt is not None else None
    # hint: could be None. handled in further process.

    # hint: in this case we need the SAP article number with leading zeros
    sap_material_number = order.sap_material
    try:
        product = SAPProduct.objects.get(sap_article_number=sap_material_number)
    except SAPProduct.DoesNotExist as exc:
        log.warning(f"Product: {sap_material_number=} does not exist. {exc=}")
        product = None

    order_book_entry = OrderBookEntry(
        ob_uid=f"{order.lstrip_sales_order()}{order.lstrip_sap_material_number()}",
        order=order,
        expected_loading_date=expected_loading_date,
        expected_loading_week=calender_week(expected_loading_date) if expected_loading_date is not None else None,
        ginger_code=order.ginger_code_17,
        sap_material=order.lstrip_sap_material_number(),
        net_volumes_sqm=round(net_volumes_sqm, 3) if isinstance(net_volumes_sqm, float) else net_volumes_sqm,
        # hint: mixed values (float, none). handled in further process.
        net_weight_to=round(net_weight_to, 2) if isinstance(net_weight_to, float) else net_weight_to,
        # hint: mixed values (float, none). handled in further process.
        volume=order.order_quantity,
        # hint: mixed values (float, none). handled in further process.
        tint=order.tint,
        thickness=order.thickness,
        coating=order.coating,  # TBD: datalake.saporder.coating sometimes has 'NONE' as string - I pass the same to output.
        sales_order=order.lstrip_sales_order(),
        ship_to_customer=order.ship_to_customer,
        ship_to_customer_name=order.customer_name,
        ship_to_country=order.country_code,
        sap_order_creation_date=order.entry_date.replace(" 00:00:00", "")
        if isinstance(order.entry_date, str)
        else order.entry_date,
        delivery_note=order.delivery_note,
        order_status=order.status,
        sub_family=order.sub_family,
        treatment=order.treatment,
        reservation_project_name=order.reservation_project_name,
        quality=order.quality,
        length=order.length.lstrip("0"),
        width=order.width.lstrip("0"),
        package_type_family=order.package_type_family,
        production_planning_class=order.production_planning_class,
        dimension_description=order.dimension_description,
        laminate=product.quality_name if product is not None else "",
        package_type_code=product.emballage_description if product is not None else "PR is None",
        stock_count=Decimal(0),
    )
    return order_book_entry


def generate_ginger_translation_dict(plant_ids: list[str]) -> dict:
    """
    Generate a translation dict from SAP material to ginger code.
    """
    translation_dict = {}
    for product in list(SAPProduct.objects.filter(plant__pk__in=plant_ids)):  # List cast -> 1 query for all products.
        translation_dict[product.lstrip_sap_material_number()] = product.ginger_code_17

    log.debug(f"generate_ginger_translation_dict(): {translation_dict=}")
    return translation_dict


def annotate_glasspanes_with_ginger_code(panes: QuerySet[GlassPane], plant_ids: list[str]) -> QuerySet[GlassPane]:
    ginger_translation: dict = generate_ginger_translation_dict(plant_ids=plant_ids)
    # Retrieve all GlassPane instances and annotate them with the corresponding ginger code
    panes = panes.annotate(
        ginger_code=Case(
            *[
                When(sap_material=sap_mat, then=Value(ginger_code))
                for sap_mat, ginger_code in ginger_translation.items()
            ],
            default=Value(None),
            output_field=CharField(),
        )
    )

    log.debug(f"annotate_glasspanes_with_ginger_code(): {list(panes)=}")
    return panes


def check_laminated_glass_delivery_time(*, expected: date, today: date, reaction_time: int) -> bool:
    if (expected - today).days - reaction_time > 0:
        return True
    return False


def _transform_orderbook_thickness(thickness: str) -> str | None:
    """thickness in orderbook has format "0590" - transform it to "5.9" """
    if thickness.isnumeric():
        return str(int(thickness) / 100)
    return None


def _get_alternate_name_of_float_product(sub_family: str) -> str | None:
    """get alternate names by sub family name - needed to work with float planners"""
    return settings.PLANT_PRODUCTION_REFERENCE.get_alternate_name_for_float_product(sub_family=sub_family)


def _get_alternate_names_of_coating_product(sub_family: str) -> list:
    """get alternate names by sub family name - needed to work with coating planners"""
    return settings.PLANT_PRODUCTION_REFERENCE.get_alternate_names_for_coating_product(sub_family=sub_family)


def _get_standing_time_of_coating_product(sub_family: str) -> int:
    """get standing time / rest time of coating product in hours"""
    return settings.PLANT_PRODUCTION_REFERENCE.get_standing_time_of_coating(sub_family=sub_family)


def is_in_past(dt: date) -> bool:
    return dt < timezone.now().date()


def add_entry_manipulate_stock(*, order_id: str, orderbook: Orderbook) -> Orderbook:
    entry: OrderBookEntry = transfer_order_to_order_book_entry(order_id=order_id)
    entry.otif_predictor = "NOK"  # This is the default value and fallback if no other value is set.

    today = timezone.now().date()

    try:
        assert entry.volume is not None, f"Order {order_id} has invalid volume order_quantity (amount of panes)"
        assert entry.net_volumes_sqm is not None, f"Order {order_id} has invalid volume in sqm"
        assert entry.net_weight_to is not None, f"Order {order_id} has invalid weight in tons"
        assert entry.expected_loading_date is not None, f"Order {order_id} has no expected loading date"
    except AssertionError as e:
        log.error(f"Order {order_id=} is invalid for entry {entry=}. {e}")
        raise InvalidOrderException(f"Order {order_id} is invalid. {e}")

    try:
        tons_on_stock = orderbook.stock[entry.ginger_code]
        log.debug(f"Article: {entry.ginger_code=} has {tons_on_stock=}.")
    except KeyError as exc:
        log.debug(f"Article: {entry.ginger_code=} not on stock. {exc=}")
        tons_on_stock = Decimal(0)
        orderbook.stock[entry.ginger_code] = tons_on_stock

    ordered_tons = to_decimal(entry.net_weight_to)
    alternate_names_coating = _get_alternate_names_of_coating_product(sub_family=entry.sub_family)
    alternate_name_float = _get_alternate_name_of_float_product(sub_family=entry.sub_family)
    thickness = _transform_orderbook_thickness(thickness=entry.thickness)
    standing_time = _get_standing_time_of_coating_product(sub_family=entry.sub_family)
    date_key: str = "date"

    # progressive substraction from stock
    # tbd: avoid substraction of treshold (0.5t) with every manipulation.
    # tbd: Where is the correct place to use treshold ???
    # orderbook.stock[entry.ginger_code] -= ordered_tons + settings.STOCK_TONS_THRESHOLD
    orderbook.stock[entry.ginger_code] -= ordered_tons

    log.debug(
        f"Article: {entry.ginger_code=} reduced stock for {ordered_tons=} to {orderbook.stock[entry.ginger_code]=}"
    )
    entry.stock_count = orderbook.stock[entry.ginger_code]

    # 1. Order is ON STOCK --> OK
    # TBD: with using Threshold here we calculate with each order 0.5t more (but from what ???).
    if orderbook.stock[entry.ginger_code] > ( 0 + settings.STOCK_THRESHOLD ):
        entry.otif_predictor = "OK"

    # 2. FLOAT PLANNING --> NP or NOK
    elif floater.product_in_float_plan(
        float_plan=orderbook.production_planner_float,
        alternate_name=alternate_name_float,
        thickness=thickness,
        lower_case=True,
    ):
        if thickness and alternate_name_float:
            possible_production_dates = floater.get_possible_float_production_dates(
                plan=orderbook.production_planner_float,
                sub_family=alternate_name_float,
                thickness=thickness,
                delivery_day=entry.expected_loading_date,
                standing_time=standing_time,
                date_key=date_key,
            )
            if possible_production_dates:
                first_production_date = possible_production_dates.pop(0)
                entry.otif_predictor = "NP"
                entry.planned_production_date = first_production_date

    # 3. COATER PLANNING --> NP or NOK
    # article is planned to be produced in future (information in COATER Production Planner (Excel File))
    elif coater.product_in_coating_plan(
        coater_plan=orderbook.production_planner_coat,
        coatings=alternate_names_coating,
        lower_case=True,
    ):
        possible_production_dates = coater.get_possible_coating_production_dates(
            plan=orderbook.production_planner_coat,
            coatings=alternate_names_coating,
            delivery_day=entry.expected_loading_date,
            standing_time=standing_time,
            date_key=date_key,
        )
        if possible_production_dates:
            first_production_date = possible_production_dates.pop(0)
            entry.otif_predictor = "NP"
            entry.planned_production_date = first_production_date

    # 4. VSG PLANNING --> NP or NOK
    # quality '22' means laminated safety glas (VSG Verbundsicherheitsglas)
    elif entry.quality == "22":
        is_producible = check_laminated_glass_delivery_time(
            expected=entry.expected_loading_date,
            today=today,
            reaction_time=settings.REACTION_TIME_LAMINATED_GLASS,
        )
        if is_producible:
            # entry.planned_production_date is already part of the entry, so need to set it here again.
            entry.otif_predictor = "NP"

    entry.planned_production_week = (
        calender_week(entry.planned_production_date) if entry.planned_production_date is not None else None
    )

    orderbook.entries.append(entry)
    return orderbook
