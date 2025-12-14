from datetime import datetime, timedelta

import pandas as pd

from django.conf import settings


def check_production_status_for_row(
    *,
    row: pd.Series,
    stock_ras: pd.DataFrame,
    current_planning: pd.DataFrame,
) -> pd.Series:
    """
    Check if order can be produced in time

        OK: Order can be supplied from stock
        NP: Order can not be supplied from stock, but can be produced in time, acording to current planning
            (ist Neuproduktionstermin vor dem erwarteten Liefertermin?)
        NOK: Order cannot be produced in time

    # FIXME: what about coating and stock_ras?
    """
    expected_loading_date = datetime.strptime(row["Expected Loading Date"], "%d.%m.%Y")
    coating = row["Coating"]
    tint_thickness = f'{row["Tint"]}{row["Nominal Thickness"]}'
    remaining_stock = row["Remaining Stock"]

    subfamily = row["Sub-Family"]

    # qualities have a two-decimal "code"
    # Q01 Spiegelqualität
    # Q03 Bauglasqualität
    # Q22 Laminierte Qualität
    # etc..
    quality = row["Quality"]

    # TODO: get_plant() is not implemented yet
    # TODO: logic for factory implementation

    # if plant:= get_plant() == "G035":
    #     # G035
    #     raise NotImplementedError("G048 not implemented yet")
    # elif get_plant() == "G036":
    #     # G048  #Torgau
    #     raise NotImplementedError("G048 not implemented yet")

    # TODO: add information from planer

    match (subfamily, coating, remaining_stock, quality):
        case (_, _, stock_after_prod, _) if stock_after_prod >= settings.STOCK_THRESHOLD:
            # OK
            # can be served from available stock
            row["OTIF Predictor"] = "OK"
            return row

        case (
            subfamily,
            _,
            _,
            _,
        ) if subfamily in settings.PLANT_PRODUCTION_REFERENCE.get_product_families_flat_glass():
            # NP
            # search for next production date in the current production-program plan
            # we select the next possible date from the current planning where we produce the same tint/thickness combination
            matching_rows = current_planning[current_planning["tint_thickness"] == tint_thickness]
            if not matching_rows.empty:
                next_production_date = matching_rows["date"].min()
                row["Planned Production Date"] = next_production_date
                row["OTIF Predictor"] = "NP"
                return row

        case (_, _, _, quality) if quality == settings.LAMINATED_SAFETY_GLASS_QUALITY:
            # quality == 22 => laminated safety glas (VSG Verbundsicherheitsglas)
            # we don't have long term production planning for VSG, so no
            # information on the 'current_planning' is available here

            if expected_loading_date > datetime.now() + timedelta(days=3):
                # we can produce in the needed reaction time => if we have more
                # than 3 days reaction time (for production and
                # authorizations), we can plan and spontaneausly produce in
                # time though
                row["OTIF Predictor"] = "NP"
                return row

        # is wärmeschutzglas, and in coatings for wäreschutzglas
        case (subfamily, coating, _, _) if settings.PLANT_PRODUCTION_REFERENCE.coating_is_produceable(
            subfamily=subfamily, coating=coating
        ):
            # everything produced on coater mag (magnetron)
            matching_rows = current_planning[current_planning["coating 1"] == coating]
            if not matching_rows.empty:
                next_production_date = matching_rows["date"].min()
                if settings.PLANT_PRODUCTION_REFERENCE.productionline_has_eclaz_coating(subfamily=subfamily):
                    # we need more time for preparation of eclaz
                    next_production_date += timedelta(hours=48)
                row["Planned Production Date"] = next_production_date
                row["OTIF Predictor"] = "NP"
                return row

    # no case matched, we cannot produce in time
    row["OTIF Predictor"] = "NOK"
    return row


def predict_otif(*, orderbook: pd.DataFrame, stock_ras: pd.DataFrame, current_planning: pd.DataFrame) -> pd.DataFrame:
    orderbook["OTIF Predictor"] = ""
    orderbook["Planned Production Date"] = ""

    orderbook = orderbook.apply(
        lambda row: check_production_status_for_row(
            row=row,
            stock_ras=stock_ras,
            current_planning=current_planning,
        ),
        axis=1,
    )
    return orderbook
