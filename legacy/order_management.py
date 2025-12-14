import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


start_time = time.time()
orderbook_new = pd.read_excel("SC_DO03 Order Management PORZ.xlsx")
orderbook_new["ob_UID"] = orderbook_new["Sales Order"].astype(str) + orderbook_new["Material Plant"].astype(str)


# Change for direct download from SAP/Datalake , create DB/DF with all orders and their status
# Merge with information of planners from previous file
orderbook_old = pd.read_excel(
    "20230418 G035 Auftragsbestand VORTAG.xlsx",
    sheet_name="Ordermanagement",
    usecols=["ob_UID", "Status", "ETD", "Comment", "NP CW"],
)
orderbook_old["ob_UID"] = orderbook_old["ob_UID"].astype(str)  # einmalig

orderbook = orderbook_new.merge(orderbook_old, on="ob_UID", how="left")
orderbook.drop_duplicates(keep="first", inplace=True, ignore_index=False)
orderbook.replace(np.nan, "", inplace=True)
# for i in orderbook.columns:
#    if orderbook[i].dtype == "datetime64[ns]":
#        orderbook[i] = orderbook[i].dt.strftime('%d.%m.%Y')
#    else: continue
orderbook = orderbook.round(2)

# Import Orion Stock, merge with Ginger Code 17 ID, group available stock by Ginger Code
orion_raw = pd.read_excel("ORION Bestand 2023_04_18.xlsx")
article_ginger = pd.read_excel(
    "000_MSTR_DATA_COUNTRY_GERMANY_Planner_aktuell.xlsx",
    sheet_name="Products",
    usecols=["Material Plant Material", "Ginger Code 17 ID"],
)
article_ginger = article_ginger.rename(
    columns={"Material Plant Material": "SAP-Produkt", "Ginger Code 17 ID": "Ginger Code 17"}
)
stock = orion_raw.merge(article_ginger, on="SAP-Produkt")[
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
    stock[stock["Qualitäts-Status"].isin(["RAS"])]
    .groupby("Ginger Code 17")
    .agg({"to": "sum", "Fläche m²": "sum", "Lagernde Menge": "sum"})
    .reset_index()
)
stock_ras.to_excel("stock_ras.xlsx", sheet_name="test", index=False)


def pplans():
    date_range = pd.date_range(datetime.now().date(), periods=365)
    pplans = pd.DataFrame(date_range, columns=["date"])

    float_plan = pd.read_excel(
        "Produktionsprogramm G035 Float.xlsx", sheet_name="Planung", usecols=["Date", "Tint", "Thickness mm"]
    )  # Sharepoint-Laufwerk
    float_plan["tint_thickness"] = float_plan["Tint"].astype(str) + float_plan["Thickness mm"].astype(str)
    float_plan["Date"] = pd.to_datetime(float_plan["Date"], format="%Y%m%d")
    float_plan.columns = float_plan.columns.str.lower()
    coater_plan = pd.read_excel(
        "Produktionsprogramm G035 MAG.xlsx", sheet_name="Planung", usecols=["date", "coating 1"]
    )  # Netzlaufwerk O:
    coater_plan["date"] = pd.to_datetime(coater_plan["date"], format="%Y%m%d")

    pplans = pplans.merge(coater_plan, on="date", how="left")
    pplans = pplans.merge(float_plan, on="date", how="left")

    return pplans


curr_planning = pplans()


def check_np(row, stock_ras, curr_planning):
    date = row["Expected Loading Date"]
    coating = row["Coating"]
    tint_thickness = row["Tint"] + str(row["Nominal Thickness"])
    remaining_stock = row["Remaining Stock"]
    subfamily = row["Sub-Family"]
    quality = row["Quality"]

    # to implement check after production version X / F, if F ==> Purchase
    if remaining_stock >= -0.5:
        return "OK"
    elif subfamily in ["DIAMANT", "PLANILUX"]:
        matching_rows = curr_planning[curr_planning["tint_thickness"] == tint_thickness]
        next_production_date = matching_rows["date"].min() if not matching_rows.empty else None
        if matching_rows.empty:
            return "NOK"
        else:
            return "NP", next_production_date
    elif quality == 22:
        if date <= datetime.now() + timedelta(days=1):
            return "NOK"
        else:
            return "NP"
    elif subfamily in ["BIOCLEAN", "ECLAZ", "PLANITHERM", "TIMELESS"] and coating in [
        "BIOCLEAN",
        "ECLAZ",
        "ECLAZ ONE",
        "PLT XN",
        "TIMELESS",
    ]:
        matching_rows = curr_planning[curr_planning["coating 1"] == coating]
        next_production_date = matching_rows["date"].min() if not matching_rows.empty else None
        if matching_rows.empty:
            return "NOK"
        else:
            if subfamily == "ECLAZ":
                next_production_date = next_production_date + timedelta(hours=48)
                return "NP", next_production_date
            else:
                return "NP", next_production_date
    else:
        return "NOK"


# Check order quantitiy vs. stock
orderbook = orderbook.merge(stock_ras, on="Ginger Code 17", how="left")

orderbook["cumsum_order"] = orderbook.groupby("Ginger Code 17")["TO"].cumsum()
orderbook["Remaining Stock"] = orderbook["to"] - orderbook["cumsum_order"]
orderbook[["OTIF Predictor", "Planned production date"]] = orderbook.apply(
    lambda row: pd.Series(check_np(row, stock_ras, curr_planning)), axis=1
)
orderbook.loc[orderbook["OTIF Predictor"] != "NP", "Planned production date"] = ""
orderbook["Planned production date"] = pd.to_datetime(orderbook["Planned production date"])
orderbook["Planned production week"] = orderbook["Planned production date"].dt.isocalendar().week

orderbook.to_excel("output.xlsx", sheet_name="Ordermanagement", index=False)

end_time = time.time()
total_time = end_time - start_time
print(total_time)
