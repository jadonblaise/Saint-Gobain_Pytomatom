import datetime
import logging

from django.utils import timezone

from apps.sharepoint.models import FloaterProductionPlanner

from . import collections, production


log = logging.getLogger("django.plans")


def _get_last_float_plan() -> list[dict]:
    """
    Load last float plan from DB.
    Returns rows as list of "entry"-dicts.
    """
    planner = FloaterProductionPlanner.objects.first()
    if planner is None:
        return []
    return planner.plan


def _get_float_product_collection(
    plan: dict,
    sub_family: str,
    thickness: str | int | float,
) -> list[dict] | None:
    """
    Fetch single product collection from float plan.

    plan:
        floater plan (third level collection)
    sub_family:
        which sub_family (known as 'tint' in planners) is desired (if not present in collection return None)
    thickness:
        which thickness is desired (if not present in collection return None)

    """
    if (product_tint := plan.get(sub_family)) is None:
        log.warning(f"Could not find {sub_family=} in passed planning collection.")
        return None

    if (product_thickness := product_tint.get(str(thickness))) is None:
        log.warning(f"Could not find {thickness=} in {sub_family=} planning collection.")
        return None

    return product_thickness


def get_float_plan() -> dict:
    """
    Get last imported float plan. Transformed.
    """
    # Load
    plan = _get_last_float_plan()
    # Prepare (reduce to needed attributes)
    log.debug(f"Prepare float plan. {len(plan)=}")
    plan = production.prepare(
        plan=plan,
        translation={
            "Date": "date",
            "Tint": "tint",
            "Thickness mm": "thickness",
            "Available\nfor Sales": "available",
        },
    )
    # Clean up - no entries older than today
    today = timezone.now().date()
    plan = production.remove_entries(plan=plan, older_than=today)  # hint: hide for tests
    # re-forming of Float plan into collection by 'tint' attribute for usage in calculation logic
    plan_2l = collections.extract_key(plan=plan, key="tint")
    # re-forming into collection with higher abstraction level
    plan_3l = collections.deep_extract(plan=plan_2l, key="thickness")
    # sorting of high level collection content by date
    return collections.sort_by_deep(plan=plan_3l, key="date", descending=False)


def check_float_production(
    plan: dict,
    sub_family: str,
    thickness: str | int | float,
    delivery_day: datetime.date,
    demanded_volume_t: float,
    puffer: float,
    standing_time: int,
    date_key: str,
    available_volume_key: str,
) -> production.PossibleProductionDate:
    """
    Check future production possibility.

    plan:
        floater plan
    sub_family:
        sub_family/tint of product
    thickness:
        thickness of product
    delivery_day:
        production must be finished until
    demanded_volume_t:
        volume to produce in tons
    puffer:
        consider puffer (e.g. broken glass)
    standing_time:
        rest time for a product after being produced
    date_key:
        column/key with production date in plan
    available_volume_key:
        column/key with production volume on this day

    """
    if (
        product_collection := _get_float_product_collection(plan=plan, sub_family=sub_family, thickness=thickness)
    ) is None:
        log.warning(f"Could not find {sub_family=} in passed planning collection.")
        return production.PossibleProductionDate()

    produceable_date = production.check_production_possibility(
        product_collection=product_collection,
        delivery_day=delivery_day,
        demanded_volume=demanded_volume_t,
        puffer=puffer,
        standing_time=standing_time,
        date_key=date_key,
        available_volume_key=available_volume_key,
    )
    return produceable_date


def product_in_float_plan(float_plan: dict, alternate_name: str | None, thickness: str | None, lower_case: bool):
    """
    Is float product member of float planner.

    technical_description:
        float product name to search for (like PLC or DIAMANT)
    thickness:
        thickness of the product to search for
    lower_case:
        True: keys in lower case format / False: no modification
    """
    if alternate_name and thickness:
        # produce dict with modified tint name as key and original tint name as its value
        descriptions = {
            (str(_description).lower() if lower_case else _description): _description
            for _description in float_plan.keys()
        }
        alternate_name = alternate_name.lower() if lower_case else alternate_name
        if alternate_name in descriptions:
            # use this original key to get the right collection to check for thickness
            thicknesses = [str(_thickness) for _thickness in float_plan[descriptions[alternate_name]]]
            if thickness in thicknesses:
                return True
    return False


def get_possible_float_production_dates(
    plan: dict,
    sub_family: str,
    thickness: str | int | float,
    delivery_day: datetime.date,
    standing_time: int,
    date_key: str,
) -> list:
    """
    Get possible production dates for float products
    - this method DOES NOT consider the volume of an order in relation to the planned capacity
    - only criteria is to check production for a defined product in time range til delivery day
    - standing time is also included in this calculation

    Args:
        plan:
            float plan (two level collection)
        sub_family:
            alternate name for float product
        delivery_day:
            expected loading day
        standing_time:
            rest time for a product after producting
        date_key:
            column name in product collection that defines production date

    Returns:
        list: found production dates
    """
    producing_days = []
    product_collection = _get_float_product_collection(plan=plan, sub_family=sub_family, thickness=thickness)
    if product_collection:
        max_producing_day = delivery_day - production.transform_standing_time_to_days(hours=standing_time)
        for plan_entry in product_collection:
            production_date = plan_entry.get(date_key, None)
            if isinstance(production_date, datetime.date) and production_date < max_producing_day:
                producing_days.append(production_date)
    return producing_days
