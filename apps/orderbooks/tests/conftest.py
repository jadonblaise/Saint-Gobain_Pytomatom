import pytest

from django.conf import settings

from apps.resources import read


@pytest.fixture
def new_orders_orderbook():
    return read.as_df(path=settings.RESOURCES_DIR / "order-management" / "SC_DO03 Order Management PORZ.xlsx")


@pytest.fixture
def old_orders_orderbook():
    return read.as_df(
        path=settings.RESOURCES_DIR / "order-management" / "G035 Auftragsbestand.xlsx",
        sheet_name="Ordermanagement",
        usecols=["ob_UID", "Status", "ETD", "Comment", "NP CW"],
    )


@pytest.fixture
def orion_raw():
    return read.as_df(path=settings.RESOURCES_DIR / "order-management" / "ORION Bestand 2023_04_11.xlsx")


@pytest.fixture
def article_ginger():
    return read.as_df(
        path=settings.RESOURCES_DIR / "order-management" / "000_MSTR_DATA_COUNTRY_GERMANY_Planner_aktuell.xlsx",
        sheet_name="Products",
        usecols=["Material Plant Material", "Ginger Code 17 ID"],
    )


@pytest.fixture
def float_plan():
    return read.as_df(
        path=settings.RESOURCES_DIR / "order-management" / "Produktionsprogramm G035 Float.xlsx",
        sheet_name="Planung",
        usecols=["Date", "Tint", "Thickness mm"],
    )


@pytest.fixture
def coater_plan():
    return read.as_df(
        path=settings.RESOURCES_DIR / "order-management" / "Produktionsprogramm G035 MAG.xlsx",
        sheet_name="Planung",
        usecols=["date", "coating 1"],
    )
