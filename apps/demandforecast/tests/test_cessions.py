from datetime import datetime

from pandas import DataFrame

from apps.demandforecast.cessions_modification import (
    check_cession_month,
    check_ratio,
    check_plant,
    check_customer,
    check_df_month,
    check_df_m2,
    reform_incoming_ratio,
    modification_through_cessions,
    SingleDemandForecast,
)
from apps.demandforecast.tests.test_values.cessions_test_values import (
    CHECK_CESSION_MONTH,
    CHECK_CESSION_PLANT,
    CHECK_CUSTOMER,
    CHECK_DF_MONTH,
    CHECK_DF_M2,
    CHECK_SINGLE_DEMAND_FORECAST_SET_PLANT1_PLANT2,
    CHECK_SINGLE_DEMAND_FORECAST_SET_M2_AND_TOTAL_M2,
    CHECK_MODIFICATION_THROUGH_CESSIONS,
    CHECK_REFORM_INCOMING_RATIO,
    DATA_TO_GENERATE_DATA_FRAMES_FOR_MODIFICATION_THROUGH_CESSIONS,
)


def test_check_cession_month():
    """test values: attr 1: formatted date time string (MM-YYYY) -
    attr 2: other month - attr 3: other year - expected value: bool"""
    test_values = CHECK_CESSION_MONTH
    for test in test_values:
        result = check_cession_month(mm_yyyy=test[0])

        assert result[0] == test[1][0]  # type: ignore
        if test[1][0]:  # type: ignore
            assert result[2].month == test[1][1]  # type: ignore
            assert result[2].year == test[1][2]  # type: ignore


def test_check_cession_ratio(cession_ratio):
    """Check if the cession_ratio matches ....TODO: mrkf : tuple[attrs, expected_result]"""
    result = check_ratio(ratio_1=cession_ratio.attrs.ratio_plant_1, ratio_2=cession_ratio.attrs.ratio_plant_2)

    sucess = result[0]
    assert sucess == cession_ratio.expected_result.success
    if sucess:
        assert (result[2], result[3], result[4]) == (
            cession_ratio.expected_result.ratio_plant_1,
            cession_ratio.expected_result.ratio_plant_2,
            cession_ratio.expected_result.ratio_total,
        )


def test_check_plant():
    """test values [attr 1, expected result]"""
    test_values = CHECK_CESSION_PLANT
    for test in test_values:
        result = check_plant(plant=test[0])  # type: ignore

        assert result == test[1]


def test_check_customers():
    """test values [attr 1, expected result]"""
    test_values = CHECK_CUSTOMER
    for test in test_values:
        result = check_customer(customer=test[0])  # type: ignore

        assert result == test[1]


def test_check_df_month():
    """test values [attr 1, expected result]"""
    test_values = CHECK_DF_MONTH
    for test in test_values:
        result = check_df_month(yyyy_mm_dd=test[0])  # type: ignore

        assert result[0] == test[1][0]
        if test[1][0]:
            assert result[2] == test[1][1]


def test_check_df_m2():
    """test values [attr 1, expected result (bool, float)]"""
    test_values = CHECK_DF_M2
    for test in test_values:
        result = check_df_m2(m2=test[0])

        assert result[0] == test[1][0]
        assert result[2] == test[1][1]


def test_set_plant1_plant2():
    """test values [attr 1, attr 2, expected result (bool, str)]"""
    test_values = CHECK_SINGLE_DEMAND_FORECAST_SET_PLANT1_PLANT2
    for test in test_values:
        obj = SingleDemandForecast()
        result = obj.set_plant1_plant2(amount_plant_1=test[0], amount_plant_2=test[1])  # type: ignore
        # print(f"{test=} {result}")
        assert result[0] == test[2][0]
        if test[2][0]:
            assert obj.plant_1_ratio == test[2][1]  # type: ignore
            assert obj.plant_2_ratio == test[2][2]  # type: ignore


def test_set_m2_and_total_m2():
    """test to set m2 and total_m2"""
    test_values = CHECK_SINGLE_DEMAND_FORECAST_SET_M2_AND_TOTAL_M2
    for test in test_values:
        obj = SingleDemandForecast()
        result = obj.set_m2_and_total_m2(total_m2=test[0], m2=test[1])  # type: ignore

        assert result[0] == test[2][0]
        if test[2][0]:
            assert obj.total_m2 == test[2][1]  # type: ignore
            assert obj.m2 == test[2][2]  # type: ignore
            assert obj.percentage_m2 == test[2][3]  # type: ignore


def test_modification_through_cessions():
    """big unit test to ensure functionality of cessions module"""
    demand_forecast_df = DataFrame(
        data=DATA_TO_GENERATE_DATA_FRAMES_FOR_MODIFICATION_THROUGH_CESSIONS["demand_forecast"]
    )
    cession_df = DataFrame(
        data=DATA_TO_GENERATE_DATA_FRAMES_FOR_MODIFICATION_THROUGH_CESSIONS["cessions_of_customers"]
    )
    demand_forecast_result, modifications, errors, _ = modification_through_cessions(
        demand_forecast_df=demand_forecast_df, cessions_df=cession_df
    )
    assert len(modifications) == 8
    assert len(errors) == 0
    for index, demand_forecast_entity in demand_forecast_result.iterrows():
        index = int(index)  # type: ignore

        assert demand_forecast_entity["LG Code"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["LG Code"]
        assert (
            datetime.combine(demand_forecast_entity["Month"].date(), demand_forecast_entity["Month"].time())
            == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["Month"]
        )
        assert (
            demand_forecast_entity["FLOW - DE - VIEW - Forecast Sales"]
            == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["FLOW - DE - VIEW - Forecast Sales"]
        )
        assert demand_forecast_entity["LGK"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["LGK"]
        assert demand_forecast_entity["Customer"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["Customer"]
        assert demand_forecast_entity["Ginger Code 17"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["Ginger Code 17"]
        assert demand_forecast_entity["m2"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["m2"]
        assert demand_forecast_entity["Total m²"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["Total m²"]
        assert demand_forecast_entity["Percentage m²"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["Percentage m²"]
        assert demand_forecast_entity["R2D2"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["R2D2"]
        assert demand_forecast_entity["C3PO"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["C3PO"]
        assert demand_forecast_entity["Shipping Plant"] == CHECK_MODIFICATION_THROUGH_CESSIONS[index]["Shipping Plant"]


def test_reform_incoming_ratio():
    """test - reform ratio to float type
    attributes of test cases: tuple[successful (bool), result (float)]"""
    test_values = CHECK_REFORM_INCOMING_RATIO
    for test_parameter, expected_return in test_values:
        expected_successful, expected_result = expected_return
        real_successful, message, real_result = reform_incoming_ratio(ratio=test_parameter)

        assert real_successful == expected_successful
        if expected_successful:
            assert real_result == expected_result
