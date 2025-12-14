from math import nan
from typing import NamedTuple

import pytest


class CessionRatioResult(NamedTuple):
    success: bool
    message: str
    ratio_plant_1: float
    ratio_plant_2: float
    ratio_total: float


class CessionRatioAttrs(NamedTuple):
    ratio_plant_1: float
    ratio_plant_2: float


class CessionRatioTest(NamedTuple):
    attrs: CessionRatioAttrs
    expected_result: CessionRatioResult


@pytest.fixture(
    params=(  # CHECK_CESSION_RATIO
        # test values [attr 1, attr 2, returned result]
        # normal values
        [1.0, 0.0, (True, "", 1.0, 0.0, 1.0)],
        [0.0, 1.0, (True, "", 0.0, 1.0, 1.0)],
        [0.5, 0.5, (True, "", 0.5, 0.5, 1.0)],
        [0.37, 0.63, (True, "", 0.37, 0.63, 1.0)],
        # too much or too low
        [1.0, 1.0, (False, "", 1.0, 1.0, 2.0)],
        [0.0, 0.0, (False, "", 0.0, 0.0, 0.0)],
        [0.7, 0.7, (False, "", 0.7, 0.7, 1.4)],
        [0.3, 0.3, (False, "", 0.3, 0.3, 0.6)],
        # border test
        [0.0, 0.99, (False, "", 0.0, 0.99, 0.99)],
        [0.0, 1.01, (False, "", 0.0, 1.01, 1.01)],
        [0.99, 0.0, (False, "", 0.99, 0.0, 0.99)],
        [1.01, 0.0, (False, "", 1.01, 0.0, 1.01)],
        [0.49, 0.5, (False, "", 0.49, 0.5, 0.99)],
        [0.51, 0.5, (False, "", 0.51, 0.5, 1.01)],
        [0.5, 0.49, (False, "", 0.5, 0.49, 0.99)],
        [0.5, 0.51, (False, "", 0.5, 0.51, 1.01)],
        # wrong types -> True -> could be parsed and the sum is correct
        ["", 1.0, (True, "", 0.0, 1.0, 1.0)],
        [1.0, "", (True, "", 1.0, 0.0, 1.0)],
        ["1", 0.0, (True, "", 1.0, 0.0, 1.0)],
        [0.0, "1", (True, "", 0.0, 1.0, 1.0)],
        ["0.5", 0.5, (True, "", 0.5, 0.5, 1.0)],
        [0.5, "0.5", (True, "", 0.5, 0.5, 1.0)],
        # wrong valus -> False -> no result
        ["abc", 1.0, (False, "", 0.0, 0.0, 0.0)],
        [1.0, "abc", (False, "", 0.0, 0.0, 0.0)],
        ["abc", "abc", (False, "", 0.0, 0.0, 0.0)],
        # wrong values -> False -> could be parsed but the sum is wrong
        ["1", 1.0, (False, "", 1.0, 1.0, 2.0)],
        [1.0, "1", (False, "", 1.0, 1.0, 2.0)],
        ["", "", (False, "", 0.0, 0.0, 0.0)],
        # negative values -> all False
        [-0.1, 0.9, (False, "", -0.1, 0.9, 0.8)],
        [0.9, -0.1, (False, "", 0.9, -0.1, 0.8)],
        [-0.5, -0.5, (False, "", -0.5, -0.5, -1.0)],
        [-0.1, 1.1, (False, "", -0.1, 1.1, 1.0)],
        [1.1, -0.1, (False, "", 1.1, -0.1, 1.0)],
        # results with NaN
        [1.0, nan, (True, "", 1.0, 0.0, 1.0)],
        [nan, 1.0, (True, "", 0.0, 1.0, 1.0)],
        [nan, nan, (False, "", 0.0, 0.0, 0.0)],
    )
)
def cession_ratio(request):
    check_cession_ration_values = request.param
    result = CessionRatioResult(
        success=check_cession_ration_values[2][0],
        message=check_cession_ration_values[2][1],
        ratio_plant_1=check_cession_ration_values[2][2],
        ratio_plant_2=check_cession_ration_values[2][3],
        ratio_total=check_cession_ration_values[2][4],
    )
    attrs = CessionRatioAttrs(
        ratio_plant_1=check_cession_ration_values[0],
        ratio_plant_2=check_cession_ration_values[1],
    )
    yield CessionRatioTest(
        attrs=attrs,
        expected_result=result,
    )
