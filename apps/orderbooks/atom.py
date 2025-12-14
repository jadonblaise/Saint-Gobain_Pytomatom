import io
from typing import NamedTuple

import pandas as pd

from django.conf import settings

from apps.orderbooks.excel_style import add_styles_to_orderbook

from ..resources import read, export
from . import transformations, predictions


class Orders(NamedTuple):
    new_orders: pd.DataFrame
    old_orders: pd.DataFrame
    orion_raw: pd.DataFrame  # raw data from orion, stock data
    article_ginger: pd.DataFrame  # code for SAP article number to ginger code
    float_plan: pd.DataFrame
    coater_plan: pd.DataFrame


def order_management_automation(
    *,
    new_orders_buffer: io.BytesIO | None = None,
    old_orders_buffer: io.BytesIO | None = None,
    orion_raw_buffer: io.BytesIO | None = None,
    article_ginger_buffer: io.BytesIO | None = None,
    float_plan_buffer: io.BytesIO | None = None,
    coater_plan_buffer: io.BytesIO | None = None,
) -> io.BytesIO:
    """
    Main function for automated order management ATOM using only the bytesIO buffers.
    """

    orders = build_orders(
        new_orders_buffer=new_orders_buffer,
        old_orders_buffer=old_orders_buffer,
        orion_raw_buffer=orion_raw_buffer,
        article_ginger_buffer=article_ginger_buffer,
        float_plan_buffer=float_plan_buffer,
        coater_plan_buffer=coater_plan_buffer,
    )
    buffered_orderbook = get_buffered_orderbook(orders=orders)
    styled_orderbook = style_orderbook(buffered_excel_file=buffered_orderbook)

    return styled_orderbook


def build_orders(
    *,
    new_orders_buffer: io.BytesIO | None = None,
    old_orders_buffer: io.BytesIO | None = None,
    orion_raw_buffer: io.BytesIO | None = None,
    article_ginger_buffer: io.BytesIO | None = None,
    float_plan_buffer: io.BytesIO | None = None,
    coater_plan_buffer: io.BytesIO | None = None,
) -> Orders:
    """
    Build the orderbook container from the bytesIO buffers.
    """
    # Sind in mapping für Datacubes enthalten.
    #
    new_orders = (
        read.as_df(path=settings.RESOURCES_DIR / "order-management" / "legacy" / "SC_DO03 Order Management PORZ.xlsx")
        if not new_orders_buffer
        else read.as_df(buffer=new_orders_buffer)
    )

    # Merge with information of planners from previous file
    old_orders = (
        read.as_df(
            path=settings.RESOURCES_DIR
            / "order-management"
            / "legacy"
            / "G035 Auftragsbestand.xlsx",
            sheet_name="Ordermanagement",
            usecols=["ob_UID", "Status", "ETD", "Comment", "NP CW"],
        )
        if not old_orders_buffer
        else read.as_df(buffer=old_orders_buffer)
    )

    orion_raw = (
        read.as_df(
            path=settings.RESOURCES_DIR / "order-management" / "legacy" / "ORION Bestand 2023_04_11.xlsx",
        )
        if not orion_raw_buffer
        else read.as_df(buffer=orion_raw_buffer)
    )

    article_ginger = (
        read.as_df(
            path=settings.RESOURCES_DIR
            / "order-management"
            / "legacy"
            / "000_MSTR_DATA_COUNTRY_GERMANY_Planner_aktuell.xlsx",
            sheet_name="Products",
            usecols=["Material Plant Material", "Ginger Code 17 ID"],
        )
        if not article_ginger_buffer
        else read.as_df(buffer=article_ginger_buffer)
    )

    # Sharepoint-Laufwerk
    float_plan = (
        read.as_df(
            path=settings.RESOURCES_DIR / "order-management" / "legacy" / "Produktionsprogramm G035 Float.xlsx",
            sheet_name="Planung",
            usecols=["Date", "Tint", "Thickness mm"],
        )
        if not float_plan_buffer
        else read.as_df(buffer=float_plan_buffer)
    )

    # Netzlaufwerk O:
    coater_plan = (
        read.as_df(
            path=settings.RESOURCES_DIR / "order-management" / "legacy" / "Produktionsprogramm G035 MAG.xlsx",
            sheet_name="Planung",
            usecols=["date", "coating 1"],
        )
        if not coater_plan_buffer
        else read.as_df(buffer=coater_plan_buffer)
    )

    return Orders(
        new_orders=new_orders,
        old_orders=old_orders,
        orion_raw=orion_raw,
        article_ginger=article_ginger,
        float_plan=float_plan,
        coater_plan=coater_plan,
    )


def get_buffered_orderbook(orders: Orders) -> io.BytesIO:
    """
    Get the buffered orderbook from the orders container.
    """
    orderbook: pd.DataFrame = predict_orders(orders=orders)
    buffered = export.to_xlsx(df=orderbook, filename="output.xlsx", buffer=True, sheet_name="Ordermanagement")
    return buffered


def style_orderbook(buffered_excel_file: io.BytesIO) -> io.BytesIO:
    orderbook_styled = add_styles_to_orderbook(buffered_file=buffered_excel_file)
    buffered = export.openpyxl_to_disk(workbook=orderbook_styled, filename="output.xlsx", buffer=True)
    return buffered


def predict_orders(*, orders: Orders) -> pd.DataFrame:
    """
    Main function for automated order management ATOM,
    expects all data prepared as df and returns the prediction df
    """
    next_orders = transformations.merge_old_orderbooks(new=orders.new_orders, old=orders.old_orders)
    # Import Orion Stock, merge with Ginger Code 17 ID, group available stock by Ginger Code
    stock_ras = transformations.merge_orion_and_article_ginger(
        orion_raw=orders.orion_raw, article_ginger=orders.article_ginger
    )

    # create dataframe for production planning for "production-lines" (to get unique tint / thickness combination) per date
    current_planning = transformations.merge_production_plans(
        float_plan=orders.float_plan, coater_plan=orders.coater_plan
    )

    # Check order quantitiy vs. stock
    orderbook = transformations.merge_stock_to_oders(next_orders=next_orders, stock_ras=stock_ras)

    # OTIF: on time in full, the whole ordered quantity be supplied in time (produce + buy-in)
    orderbook = predictions.predict_otif(orderbook=orderbook, stock_ras=stock_ras, current_planning=current_planning)
    orderbook = transformations.transform_production_dates(orderbook=orderbook)

    return orderbook
