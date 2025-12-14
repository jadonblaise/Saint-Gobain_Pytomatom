import datetime
import re

import pandas as pd


def reduce_dach_forecast(*, forecast: pd.DataFrame, lg_codes: pd.DataFrame) -> pd.DataFrame:
    """Reduce 'forecast' to defined products in 'lg_codes'"""

    mask = forecast["LG Code"].isin(lg_codes["Material LG"])
    forecast = forecast.loc[mask].copy()
    return forecast


def clean_dach_forecast(*, forecast: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the dach forecast data."""

    # Month to datetime
    forecast["Month"] = pd.to_datetime(forecast["Month"], format="%Y%m")
    # Add LGK column
    forecast["LGK"] = forecast["LG Code"].astype(str) + forecast["Real Customer"].astype(str)
    # Transform float to qm
    forecast["FLOW - DE - VIEW - Forecast Sales"] *= 10_000

    # Add a specific column for the customer, to join on these
    forecast["Customer"] = forecast["Real Customer"]

    return forecast


def clean_microstrategy_forecast(*, forecast: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the microstrategy forecast data."""
    # Emre told us via teams on "May 23, 2023", that all NaN columns should just
    # be deleted.
    forecast.dropna(axis="index", how="all", inplace=True, subset=["LG Code"])

    # LG Code remove float
    forecast["LG Code"] = forecast["LG Code"].astype(int)

    # Add columns for total and percentual sqm per LGK
    # ! Important: this percentage data basically represents the historical
    # percentage distribution (from the arithmetic mean of the last six months)
    # of individual GingerCodes on the total order of the customer.
    # [here it would of course be better to be able to divide by months etc.]
    sum_of_sqm = forecast.groupby("LGK")["m2"].transform("sum")
    forecast["Total m²"] = sum_of_sqm
    forecast["Percentage m²"] = forecast["m2"] / forecast["Total m²"]

    # transform LGK to string, so that it can be merged with the dach forecast
    forecast["LGK"] = forecast["LGK"].astype(str)

    # Add a specific column for the customer, to join on these
    forecast["Customer"] = forecast["SoldTo Customer"]

    return forecast


def merge_dach_microstrategy_forecast(
    *, dach_forecast: pd.DataFrame, microstrategy_forecast: pd.DataFrame
) -> pd.DataFrame:
    """Merge the dach and microstrategy forecast data."""
    # ! We loose all the outer data that doesn"t have a match in the other
    forecast = pd.merge(dach_forecast, microstrategy_forecast, on=["LGK", "LG Code", "Customer"], how="inner")

    # Drop the duplicate customer columns
    forecast.drop(["SoldTo Customer", "Real Customer"], axis="columns", inplace=True)
    return forecast


def get_lg_code_from_gingercode(gingercode: str) -> str:
    """Get the LG Code from the Gingercode."""
    # it is always the first six characters..
    pattern = re.compile(r"^(\w{6})")
    match = pattern.match(gingercode)
    if not match:
        raise ValueError(f"Could not extract LG Code from Gingercode {gingercode=}")
    return match.group()


def clean_shipping_plants(*, df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare the shipping plant data.
    """
    # Drop the rows where the Gingercode is "(Leer)"
    mask: pd.Series = df["Gingercode"] == "(Leer)"
    df.loc[mask] = None
    # Emre told us via teams on "May 23, 2023", that all NaN columns should just
    # be deleted.
    df.dropna(axis="index", how="all", inplace=True, subset=["Customer"])

    # Clean the float values
    df["Customer"] = df["Customer"].astype(int)
    reduced = df[["Customer", "Gingercode", "G035", "G048", "Shipping Plant"]]
    # Copy the dataframe, so that we don"t change the original, or pandas complains
    cleaned = reduced.copy()
    cleaned["LGK"] = reduced["Gingercode"].apply(get_lg_code_from_gingercode) + reduced["Customer"].astype(str)

    # Rename the gingercode to match the other dataframe
    cleaned.rename(columns={"Gingercode": "Ginger Code 17"}, inplace=True)
    return cleaned


def merge_shipping_plants(*, forecast: pd.DataFrame, shipping_plants: pd.DataFrame) -> pd.DataFrame:
    """Add the shipping plants to the forecast."""
    forecast_with_plants = pd.merge(forecast, shipping_plants, on=["LGK", "Customer", "Ginger Code 17"], how="inner")
    return forecast_with_plants


def transform_forecast_to_sap_upload(
    *, forecast: pd.DataFrame, reference_data: pd.DataFrame, which_month: int | None = None
) -> pd.DataFrame:
    """transform demand forecast output to SAP upload file

    Args:
        forecast (pd.DataFrame): demand forecast (calculated in steps before)
        reference_data (pd.DataFrame): -Stammdaten- to get Material Code of Ginger Code 17
        which_month (int | None, optional): choose month to calculate. Defaults to None.

    Returns:
        pd.DataFrame: SAP upload (dataframe)
    """
    sap_upload = _create_sap_upload_df(forecast=forecast, reference_data=reference_data)
    sap_upload = _add_weeks(sap_upload=sap_upload)
    sap_upload = _reduce_to_month(sap_upload=sap_upload, which_month=which_month)
    sap_upload = _set_material(pre_sap_upload=sap_upload, reference_data=reference_data)
    sap_upload = sap_upload.drop(["Ginger Code 17 ID"], axis=1)
    return sap_upload


# 'Ginger Code 17 ID' - must match with 'Ginger Code 17' of source
# 'Packaging ID' - must be '002'
# 'Material Plant Material' - result for column 'Material'


def _create_sap_upload_df(*, forecast: pd.DataFrame, reference_data: pd.DataFrame) -> pd.DataFrame:
    sap_upload = pd.DataFrame(index=forecast.index.copy())
    sap_upload["Material"] = pd.Series(dtype="string")
    sap_upload["Ginger Code 17 ID"] = forecast["Ginger Code 17"].copy()
    sap_upload["Plant"] = forecast["Shipping Plant"].copy()
    sap_upload["Reqmt type"] = "VSF"  # is static
    sap_upload["Version"] = [mon.month for mon in forecast["Month"]]  # column 'version' is month
    sap_upload["Active"] = "X"  # marks active products - in this case there are active products always
    sap_upload["Type"] = sap_upload["Plant"] + "_CLE"
    sap_upload["M2"] = forecast["m2"].copy()
    return sap_upload


def _add_weeks(*, sap_upload: pd.DataFrame) -> pd.DataFrame:
    for week in range(4):
        sap_upload[str(week)] = sap_upload["M2"] / 4
    return sap_upload


def _reduce_to_month(*, sap_upload: pd.DataFrame, which_month: int | None):
    which_month = (
        datetime.date.today().month if which_month is None or which_month < 1 or which_month > 12 else which_month
    )
    mask = sap_upload["Version"] == which_month
    return sap_upload.loc[mask]


def _set_material(*, pre_sap_upload: pd.DataFrame, reference_data: pd.DataFrame) -> pd.DataFrame:
    while True:
        if len(named_index_of_rows_not_set := pre_sap_upload.loc[pre_sap_upload["Material"].isnull()].index) < 1:
            break
        # get ginger and plant of first result of not already set rows
        first_named_index = named_index_of_rows_not_set[0]
        ginger_code_17 = pre_sap_upload["Ginger Code 17 ID"].loc[first_named_index]
        plant_id = pre_sap_upload["Plant"].loc[first_named_index]
        # get rows with set ginger code (only one plant with each step in loop)
        named_index_of_rows_with_this_ginger = pre_sap_upload.loc[
            (pre_sap_upload["Ginger Code 17 ID"] == ginger_code_17) & (pre_sap_upload["Plant"] == plant_id)
        ].index
        # set material code by ginger and plant id (packaging version 002 / 006 / 026) - without plant we will get more than one result eventually
        material = _get_material_code(
            ginger_code_17=ginger_code_17, reference_data=reference_data, packaging_id=2, plant_id=plant_id
        )
        if material is None:
            material = _get_material_code(
                ginger_code_17=ginger_code_17, reference_data=reference_data, packaging_id=6, plant_id=plant_id
            )
            if material is None:
                material = _get_material_code(
                    ginger_code_17=ginger_code_17, reference_data=reference_data, packaging_id=26, plant_id=plant_id
                )
                if material is None:
                    material = "N/A"
        for named_index in named_index_of_rows_with_this_ginger:
            pre_sap_upload.at[named_index, "Material"] = str(material)
    return pre_sap_upload.copy()


def _get_material_code(
    *, ginger_code_17: str, reference_data: pd.DataFrame, packaging_id: int, plant_id: str
) -> str | None:
    search_result = reference_data[
        (reference_data["Ginger Code 17 ID"] == ginger_code_17)
        & (reference_data["Packaging ID"] == packaging_id)
        & (reference_data["Plant ID"] == plant_id)
    ]
    if len(search_result) > 1:
        raise ValueError(
            f"Found more than one results in Reference Data (Stammdaten) for Ginger Code 17 '{ginger_code_17}'"
        )
    if len(search_result) < 1:
        return None
    return search_result["Material Plant Material"].iloc[0]
