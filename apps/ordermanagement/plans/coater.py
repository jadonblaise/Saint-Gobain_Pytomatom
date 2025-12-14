import datetime
import logging

from apps.sharepoint.models import CoaterProductionPlanner

from . import collections, production


log = logging.getLogger("django.plans")


def _get_last_coating_plan() -> list[dict]:
    """
    Load last coating plan from DB.
    Returns rows as list of "entry"-dicts.
    """
    planner = CoaterProductionPlanner.objects.first()
    if planner is None:
        return []
    return planner.plan


def _get_coating_collections(plan: dict[str, list], coatings: list) -> list[dict] | None:
    """
    Merges several product collections from coater plan

    plan: coater plan (second level collection)
    coatings: which coatings are desired (if not present in collection return None)

    Returns: merged collection (plan for coatings) or None
    """
    output = list()
    for coating in coatings:
        if coating:
            collection = plan.get(str(coating), None)
            if collection and isinstance(collection, list):
                output += collection
    output = collections.sort_flat(collection=output, key="date")
    return output


def get_coater_plan() -> dict[str, list[dict]]:
    # import of last coating plan
    plan = _get_last_coating_plan()
    # preparation of content (reducing to needed attributes)
    log.debug(f"Prepare coat plan. {len(plan)=}")
    plan = production.prepare(
        plan=plan,
        translation={
            "date": "date",
            "coating 1": "coating",
            "output target 1 (M²)": "available",
        },
    )
    # clean up - no entries older than today
    plan = production.remove_entries(plan=plan, older_than=datetime.date.today())  # hint: hide for tests
    # reforming of Coater plan into collection by 'coating' attribute for usage in calculation logic
    plan_2l = collections.extract_key(plan=plan, key="coating")
    # sorting of collection content by date
    return collections.sort_by(plan=plan_2l, key="date", descending=False)


def check_coating_production(
    plan: dict,
    coatings: list,
    delivery_day: datetime.date,
    demanded_volume_sqm: float,
    puffer: float,
    standing_time: int,
    date_key: str,
    available_volume_key: str,
) -> production.PossibleProductionDate:
    """
    Check future production possibility.

    plan:
        coater plan
    coatings:
        coating product names
    delivery_day:
        production must be finished until
    demanded_volume_sqm:
        volume to produce in sqm
    puffer:
        consider puffer (e.g. broken glass)
    standing_time:
        rest time for product after producing in hours
    date_key:
        column/key with production date in plan
    available_volume_key:
        column/key with production volume on this day
    """

    if (
        merged_collections := _get_coating_collections(
            plan=plan,
            coatings=coatings,
        )
    ) is None:
        log.warning(f"Could not find {coatings=} in coating plan")
        return production.PossibleProductionDate()

    produceable_date = production.check_production_possibility(
        product_collection=merged_collections,
        delivery_day=delivery_day,
        demanded_volume=demanded_volume_sqm,
        puffer=puffer,
        standing_time=standing_time,
        date_key=date_key,
        available_volume_key=available_volume_key,
    )
    return produceable_date


def product_in_coating_plan(coater_plan: dict[str, list[dict]], coatings: list, lower_case: bool) -> bool:
    """
    Is coating member of coating planner:

    coatings: name of coating to search for
    lower_case: transform keys to lower case
    """
    alternate_coating_names = [(str(coating).lower() if lower_case else coating) for coating in coatings]
    plan_coating_names = [(str(keys).lower() if lower_case else str(keys)) for keys in coater_plan.keys()]
    return bool(set(alternate_coating_names) & set(plan_coating_names))


def get_possible_coating_production_dates(
    plan: dict,
    coatings: list,
    delivery_day: datetime.date,
    standing_time: int,
    date_key: str,
) -> list:
    """
    Get possible production dates for coating products.

    - this method DOES NOT consider the volume of an order in relation to the planned capacity
    - only criteria is to check production for a defined product in time range til delivery day
    - standing time is also included in this calculation

    Args:
        plan:
            coater plan (two level collection)
        coatings:
            alternate names for coatings
        delivery_day:
            expected loading day
        standing_time:
            rest time for a product after being produced.
        date_key:
            column name in product collection that defines production date

    Returns:
        found production dates
    """
    producing_days = []
    if merged_collections := _get_coating_collections(plan=plan, coatings=coatings):
        max_producing_day = delivery_day - production.transform_standing_time_to_days(hours=standing_time)
        for plan_entry in merged_collections:
            production_date = plan_entry.get(date_key)
            if isinstance(production_date, datetime.date) and production_date < max_producing_day:
                producing_days.append(production_date)
    return producing_days
