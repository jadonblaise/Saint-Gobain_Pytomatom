import datetime
import logging
from typing import NamedTuple

from . import transform


log = logging.getLogger("django.plans")


class PossibleProductionDate(NamedTuple):
    """
    If an amount of a product is produceable.
    Date is the first possible production date.
    """

    date: datetime.date | None = None

    @property
    def produceable(self) -> bool:
        return self.date is not None


def prepare(
    *,
    plan: list[dict],
    translation: dict,
) -> list[dict]:
    """
    Preparation of loaded data for further processing.

    - plan: plan to prepare
    - translation : translate keys with {old: new}, all keys not present here will be skipped

    """

    prepared = []

    for entry in plan:
        candidate = {key: value for key, value in entry.items()}
        # Translate keys and remove all keys not present in the translation dict.
        # Should also translate lower case keys where applicable.
        candidate = transform.translate(candidate, translation=translation)
        # Transform isoformatted datetime string to date
        # ! A lot of entries are not transformed, because of NaT values.
        candidate = transform.timestamp_to_datetime(candidate, key="date")

        if not all([v is not None for v in candidate.values()]):
            # Exclude entries with missing values
            log.debug(f"Could not prepare {entry=} with {translation=}.")
            continue

        # If candidate is transformed, append it to the well prepared plans.
        prepared.append(candidate)

    log.info(f"Prepared {len(prepared)} entries from {len(plan)} entries.")
    return prepared


def _check_production_date(
    capacity: float,
    demanded_volume: float,
    puffer: float,
    volume_key: str,
    date_key: str,
    accumulated_production_days: list,
) -> PossibleProductionDate:
    """
    Check if aggregate production sum is sufficient until date

        capacity:
            aggregated volume of one product in a time span (stored in 'accumulated_production_days')
        demanded_volume:
            needed volume to finish the order
        puffer:
            small value to manage unplanned events (like broken glass etc.)
        volume_key:
            column name of volume (entry in collection)
        date_key:
            column name of date (entry in collection)
        accumulated_production_days:
            all days of production of one product until max production date to achieve the order

    """
    if capacity >= demanded_volume + puffer:
        # reversing to have last production day on top
        for production_day in reversed(accumulated_production_days):
            # take the whole volume from production_day
            demanded_volume -= production_day[volume_key]
            if demanded_volume <= 0:
                # write rest value into production_day (is pointer to original entry object of collection)
                production_day[volume_key] = round(
                    0.0 if demanded_volume == 0.0 else demanded_volume * (-1),
                    3,
                )
                if (first_production_day := production_day.get(date_key)) is None:
                    log.warning(f"No production day for {production_day=} in float planning collection.")
                    continue
                return PossibleProductionDate(date=first_production_day)
            # write zero (is empty) into production_day (is pointer to original entry object of collection)
            production_day[volume_key] = 0.0
    return PossibleProductionDate()


def _get_available_capacity(production_day: dict, key: str) -> float:
    """
    unpack value from production_day
    0.0 if value is None or not int | float
    """
    available = production_day.get(key)
    if available is None:
        log.warning(f"No value for {key=} on {production_day=} in float planning collection.")
        return 0.0

    if not isinstance(available, int) or not isinstance(available, float):
        log.warning(f"Wrong type for {available=} on {production_day=} in float planning collection.")
        return 0.0

    return available


def transform_standing_time_to_days(hours: int) -> datetime.timedelta:
    """
    Creates a timedelta in days from hours: int.

    Breaks passed value in 24 hour parts and adds 1 day for each part.
    - the last part is also one day even it has only 1 hour (e.g. 25 hours --> 2 days)
    """
    one_day_more = bool(hours % 24)
    delta = int(hours / 24) + 1 if one_day_more else int(hours / 24)
    return datetime.timedelta(days=delta)


def check_production_possibility(
    product_collection: list[dict],
    delivery_day: datetime.date,
    demanded_volume: float,
    puffer: float,
    standing_time: int = 0,
    date_key: str = "date",
    available_volume_key: str = "available",
) -> PossibleProductionDate:
    """
    Check if production until delivery_day is possible.

    - substracts needed volume from plan on the right place

    product_collection:
        collection with production days (collection from plan)
    delivery_day:
        must be produced on this day (if not, return False)
    demanded_volume:
        which amount is desired (if quantity is not sufficient until `delivery_day` return False)
    puffer:
        consider a puffer during calculation (e.g. for broken glass during transportation)
    standing_time:
        rest time for a product after producing in hours  (delivery_day - standing_time = max produceing day)
    date_key:
        key name to recognize date in collection
    available_volume_key:
        key name to recognize available volume in collection

    """
    # Accumulated production output until demand day.
    available = 0.0

    # Manage future production day capacity calculations with demands
    # higher than value of current day.
    accumulated_production_days: list = []

    for production_day in product_collection:
        if (production_date := production_day.get(date_key)) is None:
            log.warning(f"Could not work with {production_date} in {production_day} in planning collection.")
            continue

        capacity = _get_available_capacity(production_day=production_day, key=available_volume_key)
        has_to_be_produced_until = delivery_day - transform_standing_time_to_days(hours=standing_time)

        if production_date > has_to_be_produced_until:
            # No exact date match - work with entries before demand request
            produceable_date = _check_production_date(
                capacity=available,
                demanded_volume=demanded_volume,
                puffer=puffer,
                volume_key=available_volume_key,
                date_key=date_key,
                accumulated_production_days=accumulated_production_days,
            )
            return produceable_date

        # Sum up next 'available' value and append next production day
        available += capacity
        accumulated_production_days.append(production_day)

        if production_date == has_to_be_produced_until:
            # Exact date match
            produceable_date = _check_production_date(
                capacity=available,
                demanded_volume=demanded_volume,
                puffer=puffer,
                volume_key=available_volume_key,
                date_key=date_key,
                accumulated_production_days=accumulated_production_days,
            )
            return produceable_date

    return PossibleProductionDate()


def remove_entries(plan: list[dict], older_than: datetime.date, key: str = "date") -> list[dict]:
    """
    Removes all entries older than given date.
    """
    return [e for e in plan if e.get(key, None) and isinstance(e[key], datetime.date) and e[key] >= older_than]
