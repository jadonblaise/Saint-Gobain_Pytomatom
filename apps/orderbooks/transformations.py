from datetime import datetime

import pandas as pd


def add_uid_column(*, orderbook: pd.DataFrame) -> pd.DataFrame:
    orderbook["ob_UID"] = f"{orderbook['Sales Order'].astype(str)}{orderbook['Material Plant'].astype(str)}"
    return orderbook


def merge_old_orderbooks(*, old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """
    Merge old and new orderbooks
    - string convert or create the UID column
    - left join on UID
    """
    # care for uids
    new = add_uid_column(orderbook=new)
    old["ob_UID"] = old["ob_UID"].astype(str)

    # merge
    next_ = new.merge(old, on="ob_UID", how="left")

    # clean up
    next_.drop_duplicates(keep="first", inplace=True, ignore_index=False)
    next_.fillna("", inplace=True)
    # all empty strings to NaN, these are the positions for one order that has not been planned ("geprüft") yet.
    # excel adds an #NV here..

    next_ = next_.apply(lambda x: x.dt.strftime("%d.%m.%Y") if x.dtype == "datetime64[ns]" else x)
    # -> check if the datetime column already has the correct dtype
    next_ = next_.round(2)

    return next_


def merge_orion_and_article_ginger(*, orion_raw: pd.DataFrame, article_ginger: pd.DataFrame) -> pd.DataFrame:
    """
    Merge orion and article_ginger
    """
    article_ginger.rename(
        columns={"Material Plant Material": "SAP-Produkt", "Ginger Code 17 ID": "Ginger Code 17"}, inplace=True
    )
    stock = orion_raw.merge(article_ginger, on="SAP-Produkt")

    # select columns and transform
    stock[
        [
            "Lagernde Menge",
            "SAP-Produkt",
            "GBS-Status",
            "to",
            "Fläche m²",
            "Qualitäts-Status",
            "Quality Reason",
            "Sperr-Bemerkung",
            "DRG Comments",
            "Lieferung",
            "Ginger Code 17",
        ]
    ]

    stock_ras = (
        stock[stock["Qualitäts-Status"].isin(["RAS"])]  # only "free" stock / nur der freie Lagerbestand
        .groupby("Ginger Code 17")
        .agg({"to": "sum", "Fläche m²": "sum", "Lagernde Menge": "sum"})
        .reset_index()
    )

    # stock_ras.to_excel("stock_ras.xlsx", sheet_name="test", index=False)
    return stock_ras


def merge_production_plans(*, float_plan: pd.DataFrame, coater_plan: pd.DataFrame) -> pd.DataFrame:
    """
    Merge float_plan and coater_plan
    """
    date_range = pd.date_range(datetime.now().date(), periods=365)
    production_plans = pd.DataFrame(date_range, columns=["date"])

    float_plan["tint_thickness"] = float_plan["Tint"].astype(str) + float_plan["Thickness mm"].astype(str)
    float_plan["Date"] = pd.to_datetime(float_plan["Date"], format="%Y%m%d")
    float_plan.columns = float_plan.columns.str.lower()  # will also convert "Date" to "date"

    coater_plan["date"] = pd.to_datetime(coater_plan["date"], format="%Y%m%d")

    production_plans = production_plans.merge(coater_plan, on="date", how="left")
    production_plans = production_plans.merge(float_plan, on="date", how="left")

    # from ..resources import export
    # export.export.to_xlsx(df=production_plans, filename="production_plans.xlsx", buffer=False, sheet_name="test")
    # tint_thickness = nannan ??!?
    return production_plans


def merge_stock_to_oders(*, next_orders: pd.DataFrame, stock_ras: pd.DataFrame) -> pd.DataFrame:
    """
    Merge next_orderbook and stock_ras
    add cumsum_order and remaining stock
    """
    # Check order quantitiy vs. stock
    orderbook = next_orders.merge(stock_ras, on="Ginger Code 17", how="left")
    orderbook["cumsum_order"] = orderbook.groupby("Ginger Code 17")["TO"].cumsum()
    orderbook["Remaining Stock"] = orderbook["to"] - orderbook["cumsum_order"]
    return orderbook


def transform_production_dates(*, orderbook: pd.DataFrame, _format: str = "%d.%m.%Y") -> pd.DataFrame:
    """
    Transform production dates
    """
    orderbook["Planned Production Date"] = pd.to_datetime(orderbook["Planned Production Date"], format=_format)
    orderbook["Planned Production Week"] = orderbook["Planned Production Date"].dt.isocalendar().week
    orderbook["Planned Production Date"] = orderbook["Planned Production Date"].dt.strftime(_format)
    return orderbook
