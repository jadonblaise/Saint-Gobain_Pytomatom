import copy
from datetime import datetime
from decimal import Decimal
from math import isnan

from pandas import Series, DataFrame, Timestamp


# from rich import print


class SingleCession:
    """Cession class - to work well with its values."""

    def __init__(self):
        self.is_valid = False
        self.date: datetime = datetime.now()
        self.lg_code: int | float = 0
        self.customer: int | float = 0
        self.plant_1_name: str = ""
        self.ratio_1: int | float = 0
        self.plant_2_name: str = ""
        self.ratio_2: int | float = 0
        self.ratio_sum: int | float = 0
        self.index: int = -1
        self.message_log: list[str] = []
        self._log(message=f"Initialization: {type(self)=} {id(self)=}")

    def __str__(self):
        return f"""SingleCession:
            {self.is_valid=}
            {id(self)=}
            {type(self)=}
            {self.date=}
            {self.lg_code=}
            {self.customer=}
            {self.plant_1_name=}
            {self.ratio_1=}
            {self.plant_2_name=}
            {self.ratio_2=}
            {self.ratio_sum=}
            {self.message_log=}"""

    def log(self, *, message: str) -> str:
        """Append message to log field - returns passed string to use it further."""
        self.message_log.append(f"{id(self.message_log)} {message}")
        return message

    def _log(self, *, message: str) -> str:
        """ONLY INTERN - append internal message to log field - returns passed string to use it further"""
        return self.log(message=(f"INTERN: {message}"))


class SingleDemandForecast:
    """demand forecast class - to work well with its values"""

    def __init__(self):
        self.is_valid: bool = False
        self.date: datetime = datetime.now()
        self.lg_code: int | float = 0
        self.customer: int | float = 0
        self.plant_1_ratio: int | float = 0
        self.plant_2_ratio: int | float = 0
        self.shipping_plant: str = ""
        self.flow_de_view_forecast_sales: int | float = 0
        self.lgk: int | float = 0
        self.ginger_code_17: str = ""
        self.m2: int | float = 0
        self.total_m2: int | float = 0
        self.percentage_m2: float | int = 0
        self.plant_1_column_name: str = "Plant_1"
        self.plant_2_column_name: str = "Plant_2"
        self.index: int = -1
        self.message_log: list[str] = []
        self._log(message=f"Initialization: {type(self)=} {id(self)=}")

    def __str__(self):
        return f"""SingleDemandForecast:
            {self.is_valid=}
            {id(self)=}
            {type(self)=}
            {self.date=}
            {self.lg_code=}
            {self.customer=}
            {self.plant_1_ratio=}
            {self.plant_2_ratio=}
            {self.shipping_plant=}
            {self.flow_de_view_forecast_sales=}
            {self.lgk=}
            {self.ginger_code_17=}
            {self.m2=}
            {self.total_m2=}
            {self.percentage_m2=}
            {self.message_log=}"""

    def log(self, *, message: str) -> str:
        """append message to log field - returns passed string to use it further"""
        self.message_log.append(f"{id(self.message_log)} {message}")
        return message

    def _log(self, *, message: str) -> str:
        """ONLY INTERN - append internal message to log field - returns passed string to use it further"""
        return self.log(message=(f"INTERN: {message}"))

    def set_m2_and_total_m2(self, *, total_m2: int | float | Decimal, m2: int | float | Decimal) -> tuple[bool, str]:
        """set m2 and total_m2 attributes -
        starts auto calculation of percentage attribute -
        returns: tuple with operation status (bool) and message about occurring errors"""
        if not (
            isinstance(total_m2, int) or isinstance(total_m2, float) or isinstance(total_m2, Decimal)
        ) or isinstance(total_m2, bool):
            return (False, self._log(message=f"Wrong type: {total_m2=}"))
        if not (isinstance(m2, int) or isinstance(m2, float) or isinstance(m2, Decimal)) or isinstance(m2, bool):
            return (False, self._log(message=f"Wrong type: {m2=}"))
        if not total_m2 > 0:
            return (False, self._log(message=f"Can not work with values equal to or lower than zero: {total_m2=}"))
        if not m2 > 0:
            return (False, self._log(message=f"Can not work with values equal to or lower than zero: {m2=}"))
        self.percentage_m2 = round(float(1 / Decimal(total_m2) * Decimal(m2)), 5)
        self.total_m2 = float(total_m2)
        self.m2 = float(m2)
        return (True, "")

    def set_plant1_plant2(
        self,
        *,
        amount_plant_1: int | float | Decimal | None = None,
        amount_plant_2: int | float | Decimal | None = None,
    ) -> tuple[bool, str]:
        """set new amounts for plant_1 (G035) and plant_2 (G048) attribute -
        empty (None) parameter value means zero -
        AUTO calculation for other attribute without set value
        (examples: (0.5, None) -> (0.5, 0.5), (0.1, None) -> (0.1, 0.9), (1, None) -> (1, 0), (0, None) -> (0, 1) ) -
        returns: tuple with operation status (bool) and message about occurring errors"""
        auto_calculation_for = {
            self.plant_1_column_name: True if amount_plant_1 is None else False,
            self.plant_2_column_name: True if amount_plant_2 is None else False,
        }
        if amount_plant_1 is None:
            amount_plant_1 = 0
        if amount_plant_2 is None:
            amount_plant_2 = 0
        if not (
            isinstance(amount_plant_1, int) or isinstance(amount_plant_1, float) or isinstance(amount_plant_1, Decimal)
        ) or isinstance(amount_plant_1, bool):
            return (False, self._log(message=f"Wrong type: {amount_plant_1=}"))
        if not (
            isinstance(amount_plant_2, int) or isinstance(amount_plant_2, float) or isinstance(amount_plant_2, Decimal)
        ) or isinstance(amount_plant_2, bool):
            return (False, self._log(message=f"Wrong type: {amount_plant_2=}"))
        if amount_plant_1 < 0 or amount_plant_1 > 1:
            return (False, self._log(message=f"Value must be between 0 and 1: {amount_plant_1=}"))
        if amount_plant_2 < 0 or amount_plant_2 > 1:
            return (False, self._log(message=f"Value must be between 0 and 1: {amount_plant_2=}"))
        dec_plant_1 = Decimal(str(amount_plant_1))
        dec_plant_2 = Decimal(str(amount_plant_2))
        if dec_plant_1 + dec_plant_2 > 1:
            return (
                False,
                self._log(message=f"Sum of values can not be HIGHER than 1: {amount_plant_1=} {amount_plant_2=}"),
            )
        if auto_calculation_for[self.plant_1_column_name] and not auto_calculation_for[self.plant_2_column_name]:
            dec_plant_1 = Decimal(1) - dec_plant_2
        if auto_calculation_for[self.plant_2_column_name] and not auto_calculation_for[self.plant_1_column_name]:
            dec_plant_2 = Decimal(1) - dec_plant_1
        if dec_plant_1 + dec_plant_2 < 1:
            return (
                False,
                self.log(message=f"Sum of values can not be LOWER than 1: {amount_plant_1=} {amount_plant_2=}"),
            )
        self.plant_1_ratio = float(dec_plant_1)
        self.plant_2_ratio = float(dec_plant_2)
        return (
            True,
            self._log(
                message=f"New amounts for plant_1_ratio and plant_2_ratio: {self.plant_1_ratio=} {self.plant_2_ratio=}"
            ),
        )

    def get_copy(self):
        """returns a deep copy (new object) of this object"""
        new_obj = copy.deepcopy(self)
        new_obj.log(message=f"Create copy of {type(self)=} {id(self)=}")
        return new_obj

    def write_row_in(self, *, demand_forecast: DataFrame, as_new_line: bool = False) -> tuple[bool, str]:
        """set attributes of entity in Demand Forecast object -
        attr 'new_line' (bool): will append new line if True / overwrites line if False (set index id in object) -
        this method is fixed to a defined table design"""
        try:
            values = [
                self.lg_code,
                self.date,
                self.flow_de_view_forecast_sales,
                self.lgk,
                self.customer,
                self.ginger_code_17,
                self.m2,
                self.total_m2,
                self.percentage_m2,
                self.plant_1_ratio,
                self.plant_2_ratio,
                self.shipping_plant,
            ]
            demand_forecast.loc[len(demand_forecast) if as_new_line else self.index] = values  # type: ignore
        except Exception as exc:
            return (
                False,
                self._log(
                    message=f"\n{exc}\nAnything went wrong during writing Demand Forecast row (Object -> DataFrame):\nObject: {str(demand_forecast)}\nSetting: {as_new_line=}\n"
                ),
            )
        return (True, self._log(message=f"Write object in DataFrame {self.index} {as_new_line=}"))


def get_demand_forecast_column_names(*, demand_forecast_df: DataFrame) -> tuple[bool, str, str]:
    """get the name of plant_1 and plant_2 (base to work with different plants)"""
    try:
        column_headers = list(demand_forecast_df.columns.values)
        return (True, str(column_headers[9]), str(column_headers[10]))
    except Exception:
        return (False, "", "")


def check_cession_month(*, mm_yyyy) -> tuple[bool, str, datetime]:
    """check format of month - acceptable format: yyyy-mm, yyyy-m"""
    # current_month = datetime.now().month if current_month is None else current_month
    # current_year = datetime.now().year if current_year is None else current_year
    try:
        mm_yyyy = str(mm_yyyy)
        date = mm_yyyy.split("-")
        month_input = int(date[0])
        year_input = int(date[1])
        value = datetime(year_input, month_input, 1)
    except Exception as exc:
        return (False, f"{exc}\nCession Month - Wrong input format - {mm_yyyy=}", datetime.now())
    if month_input > 12 or month_input < 1:
        return (False, f"Cession Month - Wrong value for month in passed formatted date - {mm_yyyy=}", datetime.now())
    if year_input < 1 or year_input > 9999:
        return (False, f"Cession Month - Wrong value for year in passed formatted date. - {mm_yyyy=}", datetime.now())
    return (True, "", value)


def check_ratio(*, ratio_1, ratio_2) -> tuple[bool, str, float, float, float]:
    """
    check ratio - sum of both must be 1 (100%) and each one must not be lower than 0 -
    RETURN value is tuple (result is valid (bool), message, ratio 1 as float, ratio 2 as float, ratio sum as float)
    """
    try:
        ratio_1_as_float = float(ratio_1) if str(ratio_1) != "" else 0.0
        ratio_2_as_float = float(ratio_2) if str(ratio_2) != "" else 0.0
    except Exception as exc:
        return (False, f"{exc}\nRatio - ratio format is not correct", 0.0, 0.0, 0.0)
    if isnan(ratio_1_as_float):
        ratio_1_as_float = 0.0
    if isnan(ratio_2_as_float):
        ratio_2_as_float = 0.0
    ratio_sum = ratio_1_as_float + ratio_2_as_float
    if ratio_1_as_float < 0 or ratio_2_as_float < 0 or ratio_1_as_float > 1 or ratio_2_as_float > 1:
        return (
            False,
            "Ratio - ratio value is too low (negative) or too high (over 100%)",
            ratio_1_as_float,
            ratio_2_as_float,
            ratio_sum,
        )
    if ratio_sum * 100 == 100:
        return (True, "", ratio_1_as_float, ratio_2_as_float, ratio_sum)
    return (False, "Ratio - ratio sum is not 100%", ratio_1_as_float, ratio_2_as_float, ratio_sum)


def check_plant(*, plant: str) -> bool:
    """check validation of plants' names"""
    if isinstance(plant, str) and plant:
        return True
    return False


def check_customer(*, customer: int | float) -> bool:
    """check validation of Customer Code"""
    if not isinstance(customer, float) and not isinstance(customer, int):
        return False
    if isinstance(customer, bool):
        return False
    if customer < 0:
        return False
    try:
        if customer - int(customer) != 0:
            return False
    except Exception:
        return False
    return True


def check_lg_code(*, lg_code: int | float) -> bool:
    """alias of check_customer"""
    return check_customer(customer=lg_code)


def check_df_month(*, yyyy_mm_dd: str | Timestamp | datetime) -> tuple[bool, str, datetime]:
    """check and convert string to datetime - acceptable: yyyy-mm-dd, yyyy-m-d, yyyy-mm-d, yyyy-m-dd -
    also possible is pandas Timestamp or datetime (Python)"""
    if isinstance(yyyy_mm_dd, Timestamp):
        try:
            date = datetime.combine(yyyy_mm_dd.date(), yyyy_mm_dd.time())
            return (
                True,
                f"Convert Pandas Timestamp to DateTime format: {type(yyyy_mm_dd)=} {yyyy_mm_dd=} -> {type(date)=} {date=}",
                date,
            )
        except Exception as exc:
            return (
                False,
                f"{exc}\nCan not convert pandas Timestamp to datetime: {type(yyyy_mm_dd)=} {yyyy_mm_dd=}",
                datetime.now(),
            )
    if isinstance(yyyy_mm_dd, datetime):
        return (True, f"Input is already datetime: {type(yyyy_mm_dd)=} {yyyy_mm_dd=}", yyyy_mm_dd)
    try:
        yyyy_mm_dd = str(yyyy_mm_dd)
        date = datetime.strptime(yyyy_mm_dd, "%Y-%m-%d")
    except Exception as exc:
        return (False, f"{exc}\nWrong date format: {type(yyyy_mm_dd)=} {yyyy_mm_dd=}", datetime.now())
    return (True, f"Parsing of string to datetime: {type(yyyy_mm_dd)=} {yyyy_mm_dd=} -> {type(date)=} {date=}", date)


def check_df_m2(*, m2) -> tuple[bool, str, float]:
    """check whether m2 of Demand Forecast is valid."""
    try:
        m2_as_float = float(m2)
    except Exception as exc:
        return (False, f"{exc}\nm2 - Error - False - m2 format is not correct. {type(m2)=} {m2=}", 0)
    if isinstance(m2, bool):
        return (False, f"m2 - Value is bool: {type(m2)=} {m2=}", 0)
    if m2 < 0:
        return (False, f"m2 - Value is lower than zero: {type(m2)=} {m2=}", 0)
    if not m2 > 0:
        return (False, f"m2 - Value is zero: {type(m2)=} {m2=}", 0)
    return (True, f"Value is valid: {type(m2)=} {m2=}", m2_as_float)


def check_df_total_m2(*, total_m2) -> tuple[bool, str, float]:
    """is alias of 'check_df_m2' method"""
    return check_df_m2(m2=total_m2)


def month_is_equal_between(*, demand_forecast_obj: SingleDemandForecast, cession_obj: SingleCession) -> bool:
    """Demand-Forecast-Objects month attribute is equal to Cession-Objects month attribute (comparison between month-year)"""
    if (
        demand_forecast_obj.date.month == cession_obj.date.month
        and demand_forecast_obj.date.year == cession_obj.date.year
    ):
        return True
    return False


def cession_ready_for_plants(*, cession_obj: SingleCession, plant_names: list[str]) -> bool:
    """check whether passed cession is fine with passed list of names -
    to exclude cessions defined for other plants (not used in this context) -
    is basement to ensure working with more than two plants"""
    if cession_obj.plant_1_name in plant_names and cession_obj.plant_2_name in plant_names:
        return True
    return False


def modify_demand_forecast_df(
    *,
    demand_forecast_obj: SingleDemandForecast,
    demand_forecast_df: DataFrame,
    shipping_plant: str,
    amount_plant_1: int | float | Decimal | None = None,
    amount_plant_2: int | float | Decimal | None = None,
    factor_for_m2_and_total_m2: int | float | Decimal | None = None,
    as_new_line_in_df: bool = False,
) -> tuple[bool, SingleDemandForecast, DataFrame]:
    """sets attributes in passed Demand-Forecast-Object and (over)writes result in passed Demand-Forecast-DataFrame

    returns: tuple with result (bool) of method,
    SingleDemandForecast-Object (with log information),
    modified Demand-Forecast-DataFrame (if True - else not modified)

    Info: if you set 'factor_for_m2_and_total_m2' you can influence 'm2'
    and 'total_m2' value (value * factor = result) (derived from ratio),
    without set 'm2' and 'total_m2' will be untouched"""
    m2 = Decimal(demand_forecast_obj.m2)
    total_m2 = Decimal(demand_forecast_obj.total_m2)
    if m2 and total_m2 and factor_for_m2_and_total_m2:
        factor = Decimal(factor_for_m2_and_total_m2)
        result, _ = demand_forecast_obj.set_m2_and_total_m2(
            total_m2=factor * Decimal(total_m2), m2=factor * Decimal(m2)
        )
        if not result:
            demand_forecast_obj.log(message=f"Not possible to set 'm2' and 'total_m2' {factor=} {m2=} {total_m2}")
            return (False, demand_forecast_obj, demand_forecast_df)
    result, _ = demand_forecast_obj.set_plant1_plant2(amount_plant_1=amount_plant_1, amount_plant_2=amount_plant_2)
    if result:
        demand_forecast_obj.shipping_plant = shipping_plant
    else:
        return (False, demand_forecast_obj, demand_forecast_df)
    result, _ = demand_forecast_obj.write_row_in(demand_forecast=demand_forecast_df, as_new_line=as_new_line_in_df)
    if result:
        return (True, demand_forecast_obj, demand_forecast_df)
    return (False, demand_forecast_obj, demand_forecast_df)


def ratio_is_1_and_plant_name_is_equal_to(*, plant_name: str, cession_obj: SingleCession) -> bool:
    """if ratio of one plant is 1 (other one is 0) and defined plant in passed cession is member of passed name list -> True else False"""
    if (cession_obj.ratio_1 == 1 and cession_obj.plant_1_name == plant_name and cession_obj.ratio_2 == 0) or (
        cession_obj.ratio_2 == 1 and cession_obj.plant_2_name == plant_name and cession_obj.ratio_1 == 0
    ):
        return True
    return False


def get_relevant_demand_forecast_entities(*, demand_forecast: DataFrame, cession_obj: SingleCession) -> DataFrame:
    """returns a DataFrame which match with settings in passed cession"""
    return demand_forecast.loc[
        (demand_forecast["LG Code"] == cession_obj.lg_code) & (demand_forecast["Customer"] == cession_obj.customer)
    ]


def reform_incoming_ratio(*, ratio) -> tuple[bool, str, float]:
    """in excel files every value will be except in default setting of sheet -
    so it could be possible to insert '12,8' instead of '12.8' (the difference is the comma instead a point) -
    trial to passing the first value to float ends in an TypeError Exception - this method tries to avoid this -

    RETURNS a tuple with (successful (bool), message (str), result (float))"""
    temp_error_message = ""
    if isinstance(ratio, bool):
        return (False, " -1- Do not use boolean values for ratio", 0.0)
    if isinstance(ratio, int) or isinstance(ratio, float):
        return (True, "", float(ratio))
    try:
        new_1_ratio = float(ratio)
        return (True, f"Convert {type(ratio)=} {ratio=} to {type(new_1_ratio)=} {new_1_ratio=}", new_1_ratio)
    except ValueError as exc:
        temp_error_message = " -1- " + str(exc)
    except TypeError as exc:
        temp_error_message = " -1- " + str(exc)
    try:
        new_2_ratio = float(str(ratio).replace(",", ".").replace("%", "").replace(" ", ""))
        new_2_ratio = 0.0 if new_2_ratio == 0 else float(Decimal(str(new_2_ratio)) / 100)
        return (
            True,
            f"Reform Incoming Ratio: {temp_error_message} -- Convert {type(ratio)=} {ratio=} to {type(new_2_ratio)=} {new_2_ratio=}",
            new_2_ratio,
        )
    except TypeError as exc:
        temp_error_message += " -2- " + str(exc)
    except ValueError as exc:
        temp_error_message += " -2- " + str(exc)
    return (False, f"Reform Incoming Ratio: \n{temp_error_message} -- {ratio=} {type(ratio)}", 0.0)


# validation of cession
def cession_validation(*, cession_series: Series, index) -> tuple[str, SingleCession]:
    """validation of cession entity (pandas series) -
    returns a SingleCession object -
    find validation status in returned object (.is_valid)"""

    cession_obj = SingleCession()

    try:
        month = cession_series["Month"]
        lg_code = cession_series["LG Code"]
        customer = cession_series["Customer"]
        plant_1_name = cession_series["Shipping Plant 1"]
        ratio_1 = cession_series["ratio SP1"]
        plant_2_name = cession_series["Shipping Plant 2"]
        ratio_2 = cession_series["ratio SP2"]
        index = int(index)
    except Exception as exc:
        cession_obj.log(
            message=f"{exc}\none or more attributes are absent in session series. {type(cession_series)=} {cession_series=} {type(index)=} {index=}"
        )
        return (str(cession_obj.message_log), cession_obj)
    month_is_valid, message, date = check_cession_month(mm_yyyy=month)
    if not month_is_valid:
        cession_obj.log(message=f"Month: {message}, {month} {type(month)}")
        return (str(cession_obj.message_log), cession_obj)
    if not check_plant(plant=plant_1_name) or not check_plant(plant=plant_2_name):
        cession_obj.log(
            message=f"wrong Plant format: '{plant_1_name}' {type(plant_1_name)}, '{plant_2_name}' {type(plant_2_name)}"
        )
        return (str(cession_obj.message_log), cession_obj)
    if plant_1_name == plant_2_name:
        cession_obj.log(message=f"Plants on both sides are the same: {plant_1_name} {plant_2_name}")
        return (str(cession_obj.message_log), cession_obj)
    if not check_customer(customer=customer):
        cession_obj.log(message=f"wrong Customer format: {customer} {type(customer)}")
        return (str(cession_obj.message_log), cession_obj)
    if not check_lg_code(lg_code=lg_code):
        cession_obj.log(message=f"wrong Customer format: {customer} {type(customer)}")
        return (str(cession_obj.message_log), cession_obj)
    ratio_is_valid, message, ratio_1, ratio_2, ratio_sum = check_ratio(
        ratio_1=reform_incoming_ratio(ratio=ratio_1)[2], ratio_2=reform_incoming_ratio(ratio=ratio_2)[2]
    )
    if not ratio_is_valid:
        cession_obj.log(message=f"ratio is not valid: {message} | {ratio_1} + {ratio_2} = {ratio_sum}")
        return (str(cession_obj.message_log), cession_obj)

    cession_obj.date = date
    cession_obj.lg_code = lg_code
    cession_obj.customer = customer
    cession_obj.plant_1_name = plant_1_name
    cession_obj.ratio_1 = ratio_1
    cession_obj.plant_2_name = plant_2_name
    cession_obj.ratio_2 = ratio_2
    cession_obj.ratio_sum = ratio_sum
    cession_obj.index = index
    cession_obj.is_valid = True

    cession_obj.log(message=f"Set attributes: {str(cession_obj)}")

    return ("Cession is valid", cession_obj)


def demand_forecast_validation(
    *, demand_forecast_series: Series, index, column_name_plant_1: str, column_name_plant_2: str
) -> tuple[str, SingleDemandForecast]:
    """validation of Demand Forecast entity (pandas series) -
    returns a SingleDemandForecast object -
    find validation status in returned object (.is_valid) -
    parameters 'column_name_plant_X' set name of used plants
    (same as values of Demand Forecast DateFrame where the passed Series is from)
    (this ensures usage of more than two plants in future)"""

    demand_forecast_obj = SingleDemandForecast()

    try:
        lg_code = demand_forecast_series["LG Code"]
        month = demand_forecast_series["Month"]
        flow_de_view_forecast_sales = demand_forecast_series["FLOW - DE - VIEW - Forecast Sales"]
        lgk = demand_forecast_series["LGK"]
        customer = demand_forecast_series["Customer"]
        ginger_code_17 = demand_forecast_series["Ginger Code 17"]
        m2 = demand_forecast_series["m2"]
        total_m2 = demand_forecast_series["Total m²"]
        percentage_m2 = demand_forecast_series["Percentage m²"]
        plant_1_ratio = demand_forecast_series[column_name_plant_1]
        plant_2_ratio = demand_forecast_series[column_name_plant_2]
        shipping_plant = demand_forecast_series["Shipping Plant"]
        index = int(index)
    except Exception as exc:
        demand_forecast_obj.log(
            message=f"{exc}\none or more attributes are absent in Demand Forecast series. {type(demand_forecast_series)=} {demand_forecast_series=} {type(index)=} {index=}"
        )
        return (str(demand_forecast_obj.message_log), demand_forecast_obj)
    month_is_valid, message, date = check_df_month(yyyy_mm_dd=month)
    if not month_is_valid:
        demand_forecast_obj.log(message=f"wrong Month format: {message}")
        return (str(demand_forecast_obj.message_log), demand_forecast_obj)
    m2_is_valid, message, m2 = check_df_m2(m2=m2)
    if not m2_is_valid:
        demand_forecast_obj.log(message=f"not possible to work with 'm2' of Demand Forecast: {message}")
        return (str(demand_forecast_obj.message_log), demand_forecast_obj)
    total_m2_is_valid, message, total_m2 = check_df_total_m2(total_m2=total_m2)
    if not total_m2_is_valid:
        demand_forecast_obj.log(message=f"not possible to work with 'Total m2' of Demand Forecast: {message}")
        return (str(demand_forecast_obj.message_log), demand_forecast_obj)
    if not check_customer(customer=customer):
        demand_forecast_obj.log(message=f"wrong Customer format in Demand Forecast: {customer} {type(customer)}")
        return (str(demand_forecast_obj.message_log), demand_forecast_obj)
    if not check_lg_code(lg_code=lg_code):
        demand_forecast_obj.log(message=f"wrong LG code format in Demand Forecast: {lg_code} {type(lg_code)}")
        return (str(demand_forecast_obj.message_log), demand_forecast_obj)

    demand_forecast_obj.date = date
    demand_forecast_obj.lg_code = lg_code
    demand_forecast_obj.flow_de_view_forecast_sales = flow_de_view_forecast_sales
    demand_forecast_obj.lgk = lgk
    demand_forecast_obj.customer = customer
    demand_forecast_obj.ginger_code_17 = ginger_code_17
    demand_forecast_obj.m2 = m2
    demand_forecast_obj.total_m2 = total_m2
    demand_forecast_obj.percentage_m2 = percentage_m2
    demand_forecast_obj.plant_1_ratio = plant_1_ratio
    demand_forecast_obj.plant_2_ratio = plant_2_ratio
    demand_forecast_obj.shipping_plant = shipping_plant
    demand_forecast_obj.plant_1_column_name = column_name_plant_1
    demand_forecast_obj.plant_2_column_name = column_name_plant_2
    demand_forecast_obj.index = index
    demand_forecast_obj.is_valid = True

    demand_forecast_obj.log(message=f"Set attributes: {demand_forecast_obj.__str__()}")

    return ("Demand Forecast series is valid", demand_forecast_obj)


def modification_through_cessions(
    *, demand_forecast_df: DataFrame, cessions_df: DataFrame
) -> tuple[DataFrame, list[dict], list[dict], list[str]]:
    """## modify Demand-Forecast-DataFrame with Cessions of Customers
    set with 'name_for_plant_X' the name of plants used in the current Demand-Forecast-DataFrame ->
    so it is possible to use other plants with this module (and do not to be fixed on two defined plants like G035 and G048)
    returns: tuple with modified Demand-Forecast-DataFrame,
    list with result of algorithm if result is well,
    list with result of algorithm if result is bad,
    list with other messages to understand what happens in this module (comes soon)
    """
    modification_counter: list[dict] = []
    error_counter: list[dict] = []
    message_log: list[str] = []
    i_have_the_names_of_plants, name_for_plant_1, name_for_plant_2 = get_demand_forecast_column_names(
        demand_forecast_df=demand_forecast_df
    )
    if i_have_the_names_of_plants:
        for cession_index, cession_series in cessions_df.iterrows():
            _, cession_obj = cession_validation(cession_series=cession_series, index=cession_index)
            if cession_obj.is_valid and cession_ready_for_plants(
                cession_obj=cession_obj, plant_names=[name_for_plant_1, name_for_plant_2]
            ):
                relevant_demand_forecast_entities = get_relevant_demand_forecast_entities(
                    demand_forecast=demand_forecast_df, cession_obj=cession_obj
                )
                for demand_forecast_index, demand_forecast_series in relevant_demand_forecast_entities.iterrows():
                    _, demand_forecast_obj = demand_forecast_validation(
                        demand_forecast_series=demand_forecast_series,
                        index=demand_forecast_index,
                        column_name_plant_1=name_for_plant_1,
                        column_name_plant_2=name_for_plant_2,
                    )
                    if demand_forecast_obj.is_valid and month_is_equal_between(
                        demand_forecast_obj=demand_forecast_obj, cession_obj=cession_obj
                    ):
                        if ratio_is_1_and_plant_name_is_equal_to(plant_name=name_for_plant_1, cession_obj=cession_obj):
                            result, obj, _ = modify_demand_forecast_df(
                                demand_forecast_obj=demand_forecast_obj,
                                demand_forecast_df=demand_forecast_df,
                                shipping_plant=name_for_plant_1,
                                amount_plant_1=1,
                            )
                        elif ratio_is_1_and_plant_name_is_equal_to(
                            plant_name=name_for_plant_2, cession_obj=cession_obj
                        ):
                            result, obj, _ = modify_demand_forecast_df(
                                demand_forecast_obj=demand_forecast_obj,
                                demand_forecast_df=demand_forecast_df,
                                shipping_plant=name_for_plant_2,
                                amount_plant_2=1,
                            )
                        elif cession_obj.ratio_1 != 1 and cession_obj.ratio_2 != 1:
                            demand_forecast_obj_second = demand_forecast_obj.get_copy()
                            result, obj, _ = modify_demand_forecast_df(
                                demand_forecast_obj=demand_forecast_obj,
                                demand_forecast_df=demand_forecast_df,
                                shipping_plant=cession_obj.plant_1_name,
                                amount_plant_1=1 if cession_obj.plant_1_name == name_for_plant_1 else 0,
                                factor_for_m2_and_total_m2=cession_obj.ratio_1,
                            )
                            result, obj, _ = modify_demand_forecast_df(
                                demand_forecast_obj=demand_forecast_obj_second,
                                demand_forecast_df=demand_forecast_df,
                                shipping_plant=cession_obj.plant_2_name,
                                amount_plant_1=1 if cession_obj.plant_1_name == name_for_plant_2 else 0,
                                factor_for_m2_and_total_m2=cession_obj.ratio_2,
                                as_new_line_in_df=True,
                            )
                        else:
                            result = False
                            obj = demand_forecast_obj
                        temp = {"index": obj.index, "message": obj.message_log}
                        if result:
                            modification_counter.append(temp)
                        elif not result:
                            error_counter.append(temp)
    return (demand_forecast_df, modification_counter, error_counter, message_log)
