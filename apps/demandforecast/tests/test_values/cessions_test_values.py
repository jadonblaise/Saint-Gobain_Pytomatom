from datetime import datetime, time
from math import nan


_date_now = datetime.now()
_day = _date_now.day
_month = _date_now.month
_year = _date_now.year


CHECK_REFORM_INCOMING_RATIO = (
    # standard values
    (42, (True, 42.0)),
    (42.7, (True, 42.7)),
    (42.0, (True, 42.0)),
    (0, (True, 0.0)),
    (0.0, (True, 0.0)),
    (-42, (True, -42.0)),
    (-42.7, (True, -42.7)),
    (-42.0, (True, -42.0)),
    (0.424242, (True, 0.424242)),
    (-0.424242, (True, -0.424242)),
    # border
    (0.1, (True, 0.1)),
    (-0.1, (True, -0.1)),
    (1, (True, 1.0)),
    (-1, (True, -1.0)),
    # strings in int or float format
    ("42", (True, 42.0)),
    ("42.7", (True, 42.7)),
    ("42.0", (True, 42.0)),
    ("-42", (True, -42.0)),
    ("-42.7", (True, -42.7)),
    ("-42.0", (True, -42.0)),
    # border
    ("0.1", (True, 0.1)),
    ("0", (True, 0.0)),
    ("-0.1", (True, -0.1)),
    ("1", (True, 1.0)),
    ("-1", (True, -1.0)),
    # wrong string format but trial to reform (the detail is the comma instead the point)
    # in this case method divides incoming value by 100
    ("42,0", (True, 0.42)),
    ("42,7", (True, 0.427)),
    ("42,", (True, 0.42)),
    ("-42,0", (True, -0.42)),
    ("-42,7", (True, -0.427)),
    ("-42,", (True, -0.42)),
    ("42,0%", (True, 0.42)),
    ("42,7%", (True, 0.427)),
    ("42,%", (True, 0.42)),
    ("-42,0%", (True, -0.42)),
    ("-42,7%", (True, -0.427)),
    ("-42,%", (True, -0.42)),
    # border
    ("0,1", (True, 0.001)),
    ("0,1%", (True, 0.001)),
    ("-0,1", (True, -0.001)),
    ("-0,1%", (True, -0.001)),
    ("0,", (True, 0.0)),
    ("0%", (True, 0.0)),
    ("0,%", (True, 0.0)),
    ("0,1", (True, 0.001)),
    ("0,1%", (True, 0.001)),
    ("-0,", (True, 0.0)),
    ("-0%", (True, 0.0)),
    ("-0,%", (True, 0.0)),
    ("-0,1", (True, -0.001)),
    ("-0,1%", (True, -0.001)),
    ("1%", (True, 0.01)),
    ("1,", (True, 0.01)),
    ("1,%", (True, 0.01)),
    ("-1%", (True, -0.01)),
    ("-1,", (True, -0.01)),
    ("-1,%", (True, -0.01)),
    # wrong values
    ("", (False, 0.0)),
    ("a", (False, 0.0)),
    ("abcd", (False, 0.0)),
    ("1ab", (False, 0.0)),
    (True, (False, 0.0)),
    (False, (False, 0.0)),
    (None, (False, 0.0)),
    ("%%,,42,,%%", (False, 0.42)),
    (", % , 42,7 , % ,", (False, 0.427)),
)


CHECK_DF_MONTH = (
    # test values [attr 1, returned result]
    # normal values
    ("2012-12-24", (True, datetime(2012, 12, 24))),
    ("2012-01-01", (True, datetime(2012, 1, 1))),
    ("2012-12-31", (True, datetime(2012, 12, 31))),
    ("2012-08-08", (True, datetime(2012, 8, 8))),
    ("0001-01-01", (True, datetime(1, 1, 1))),
    ("9999-12-31", (True, datetime(9999, 12, 31))),
    ("2012-02-29", (True, datetime(2012, 2, 29))),
    ("2012-8-04", (True, datetime(2012, 8, 4))),
    ("2012-08-4", (True, datetime(2012, 8, 4))),
    ("2012-8-4", (True, datetime(2012, 8, 4))),
    # test with date which is already datetime
    (_date_now, (True, _date_now)),
    # invalid values
    ("0-01-01", (False, None)),
    ("10000-01-01", (False, None)),
    ("2012-08-00", (False, None)),
    ("2012-00-04", (False, None)),
    ("0000-08-04", (False, None)),
    ("2012-13-04", (False, None)),
    ("2012-08-32", (False, None)),
    ("2012-02-30", (False, None)),
    ("2013-02-29", (False, None)),
    ("12-08-04", (False, None)),
    ("20120804", (False, None)),
    ("2012.08.04", (False, None)),
    ("2012--08--04", (False, None)),
    ("-2012-08-04", (False, None)),
    ("2012-08-04-", (False, None)),
    ("abcd-08-04", (False, None)),
)


CHECK_CUSTOMER = (
    # test values [attr 1, returned result]
    # normal values
    (12345, True),
    (12345.0, True),
    (0, True),
    (0.0, True),
    # wrong formats
    (12345.8, False),
    (12345.3, False),
    (12345.00001, False),
    (12345.99999, False),
    (0.01, False),
    (-0.01, False),
    (-12345, False),
    (-12345.3, False),
    (-12345.00001, False),
    (-12345.99990, False),
    ("", False),
    ("12345", False),
    (True, False),
    (None, False),
    (nan, False),
)


CHECK_CESSION_PLANT = (
    # test values [attr 1, returned result]
    # normal values
    ("G035", True),
    ("aabbccddee", True),
    # wrong formats
    ("", False),
    (23, False),
    (True, False),
    (None, False),
    (12.5, False),
)


CHECK_CESSION_MONTH = (
    # test values: attr 1: formatted date time string (MM-YYYY) -
    # attr 2: other month - attr 3: other _year - returned value: bool
    # test with fake month and fake year and leading zero for month
    ("02-2024", (True, 2, 2024)),
    # test with fake month and fake year without leading zero
    ("2-2024", (True, 2, 2024)),
    # test with fake month and fake year (two letters for month)
    ("10-2024", (True, 10, 2024)),
    # test with leading and ending spaces
    (" 10-2024", (True, 10, 2024)),
    ("10-2024 ", (True, 10, 2024)),
    (" 10 - 2024 ", (True, 10, 2024)),
    ("  10  -  2024  ", (True, 10, 2024)),
    # quaint value but valid
    ("10-1", (True, 10, 1)),
    ("10-9999", (True, 10, 9999)),
    # wrong formates
    ("10-0", (False, 0, 0)),
    ("10-10000", (False, 0, 0)),
    ("X10-2024", (False, 0, 0)),
    ("10-2024X", (False, 0, 0)),
    ("X 10-2024", (False, 0, 0)),
    ("10-2024 X", (False, 0, 0)),
    ("10X2024", (False, 0, 0)),
    ("10X-2024", (False, 0, 0)),
    ("10-X2024", (False, 0, 0)),
    ("X-2024", (False, 0, 0)),
    ("0-2024", (False, 0, 0)),
    ("100-2024", (False, 0, 0)),
    ("10--2024", (False, 0, 0)),
    ("102024", (False, 0, 0)),
    ("0-0", (False, 0, 0)),
    ("0-2024", (False, 0, 0)),
    ("13-2024", (False, 0, 0)),
)


CHECK_DF_M2 = (
    # right format
    (42, (True, 42.0)),
    (42.0, (True, 42.0)),
    (0.1, (True, 0.1)),
    (1, (True, 1.0)),
    # wrong format
    (-42, (False, 0.0)),
    (-0.1, (False, 0.0)),
    (0, (False, 0.0)),
    ("", (False, 0.0)),
    (True, (False, 0.0)),
    (False, (False, 0.0)),
    (None, (False, 0.0)),
)


# test values for method 'set_g035_g048()' in class 'SingleDemandForecast' in cessions module
CHECK_SINGLE_DEMAND_FORECAST_SET_PLANT1_PLANT2 = (
    # Correct values -> True
    (1, 0, (True, 1, 0)),
    (0, 1, (True, 0, 1)),
    (0.5, 0.5, (True, 0.5, 0.5)),
    (0.33333, 0.66667, (True, 0.33333, 0.66667)),
    (0.00001, 0.99999, (True, 0.00001, 0.99999)),
    (1, None, (True, 1, 0)),
    (None, 1, (True, 0, 1)),
    (0.5, None, (True, 0.5, 0.5)),
    (None, 0.5, (True, 0.5, 0.5)),
    (0.2, None, (True, 0.2, 0.8)),
    (None, 0.2, (True, 0.8, 0.2)),
    (0, None, (True, 0, 1, 1)),
    (None, 0, (True, 1, 0, 1)),
    # Wrong values -> False
    (1, 1, (False,)),
    (0, 0, (False,)),
    (None, None, (False,)),
    # Border Test
    (1.00001, 0, (False,)),
    (0, 1.00001, (False,)),
    (0, 0.00001, (False,)),
    (0.00001, 0, (False,)),
    (0.5, 0.49999, (False,)),
    (0.49999, 5, (False,)),
    (0.5, 0.50001, (False,)),
    (0.500001, 0.5, (False,)),
    # wrong types
    ("1", None, (False,)),
    (None, "1", (False,)),
    ("1", "1", (False,)),
    (True, None, (False,)),
    (None, True, (False,)),
    (True, True, (False,)),
)


# test values for method 'set_m2_and_total_m2()' in class 'SingleDemandForecast' in cessions module
CHECK_SINGLE_DEMAND_FORECAST_SET_M2_AND_TOTAL_M2 = (
    # (attr1: total_m2, attr2: m2, expected_result: (bool, total_m2, m2, percentage))
    # Correct values -> True
    (5000, 5000, (True, 5000, 5000, 1)),
    (5000, 4000, (True, 5000, 4000, 0.8)),
    (5000, 500, (True, 5000, 500, 0.1)),
    (5000, 50, (True, 5000, 50, 0.01)),
    (5000, 5, (True, 5000, 5, 0.001)),
    (5000, 6000, (True, 5000, 6000, 1.2)),
    # Wrong value -> False
    (0, 5000, (False,)),
    (5000, 0, (False,)),
    (0, 0, (False,)),
    (None, 5000, (False,)),
    (5000, None, (False,)),
    (True, 5000, (False,)),
    (5000, False, (False,)),
    ("1000", 5000, (False,)),
    (5000, "1000", (False,)),
)


DATA_TO_GENERATE_DATA_FRAMES_FOR_MODIFICATION_THROUGH_CESSIONS = {
    "demand_forecast": {
        "LG Code": [  # int64
            111111,
            111111,
            111111,
            111111,
            111111,
            # ---
            222222,
            222222,
            # ---
            333333,
            333333,
            # ---
            444444,
            444444,
            # ---
            999951,
            999952,
            999953,
            999954,
            999955,
        ],
        "Month": [  # datetime64[ns]
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            # ---
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            # ---
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            # ---
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime(2013, 12, 11, 0, 0, 0, 0),
            # ---
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
            datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        ],
        "FLOW - DE - VIEW - Forecast Sales": [  # float64
            1234.123456,  # not relevant
            1234.123456,
            1234.123456,
            1234.123456,
            1234.123456,
            # ---
            1234.123456,
            1234.123456,
            # ---
            1234.123456,
            1234.123456,
            # ---
            1234.123456,
            1234.123456,
            # ---
            1234.123456,
            1234.123456,
            1234.123456,
            1234.123456,
            1234.123456,
        ],
        "LGK": [  # int64
            123456789012,  # not relevant
            123456789012,
            123456789012,
            123456789012,
            123456789012,
            # ---
            123456789012,
            123456789012,
            # ---
            123456789012,
            123456789012,
            # ---
            123456789012,
            123456789012,
            # ---
            123456789012,
            123456789012,
            123456789012,
            123456789012,
            123456789012,
        ],
        "Customer": [  # int64
            100001,
            500005,
            100001,
            200002,
            500005,
            # ---
            100001,
            200002,
            # ---
            300003,
            500005,
            # ---
            400004,
            400004,
            # ---
            900009,
            900009,
            900009,
            900009,
            900009,
        ],
        "Ginger Code 17": [  # object
            "123456Q99X1111x9999L12345678",  # not relevant
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            # ---
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            # ---
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            # ---
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            # ---
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
            "123456Q99X1111x9999L12345678",
        ],
        "m2": [  # float64
            16000.00,  # other value 40%
            54321.00,  # other value 100%
            12345.67,
            12345.67,
            12345.67,
            # ---
            10000.00,
            50000.50,
            # ---
            10000.00,
            20000.00,
            # ---
            30000.00,
            40000.00,
            # ---
            10000.00,
            10000.00,
            10000.00,
            10000.00,
            10000.00,
        ],
        "Total m²": [  # float64
            40000.00,
            54321.00,
            12345.67,
            12345.67,
            12345.67,
            # ---
            1000.00,
            50000.50,
            # ---
            10000.00,
            20000.00,
            # ---
            90000.00,
            40000.00,
            # ---
            10000.00,
            10000.00,
            10000.00,
            10000.00,
            10000.00,
        ],
        "Percentage m²": [  # float64
            0.4,
            1,
            1,
            1,
            1,
            # ---
            0.1,
            1,
            # ---
            1,
            1,
            # ---
            0.33333,
            1,
            # ---
            1,
            1,
            1,
            1,
            1,
        ],
        "R2D2": [  # float64
            0,
            0.2,
            0.5,
            0.8,
            1,
            # ---
            0.33333,
            1,
            # ---
            0.5,
            0.2,
            # ---
            0.1,
            0,
            # ---
            0,
            0.2,
            0.5,
            0.8,
            1,
        ],
        "C3PO": [  # float64
            1,
            0.8,
            0.5,
            0.2,
            0,
            # ---
            0.66667,
            0,
            # ---
            0.5,
            0.8,
            # ---
            0.9,
            1,
            # ---
            1,
            0.8,
            0.5,
            0.2,
            0,
        ],
        "Shipping Plant": [  # object
            "C3PO",  # 1 for ratio defines the plant - for odd values it is variable
            "R2D2",
            "C3PO",
            "R2D2",
            "R2D2",
            # ---
            "C3PO",
            "R2D2",
            # ---
            "C3PO",
            "R2D2",
            # ---
            "C3PO",
            "C3PO",
            # ---
            "C3PO",
            "R2D2",
            "C3PO",
            "R2D2",
            "R2D2",
        ],
    },
    # Customer float64 	100011.0
    # Month	object  09-2023
    # LG Code	float64  105526.0
    # Shipping Plant 1	object  G035
    # ratio SP1	object  0.5
    # Shipping Plant 2 object  G048
    # ratio SP2  object  0.5
    "cessions_of_customers": {
        "Customer": [  # float64
            # test with right values
            100001.0,
            200002.0,
            200002.0,
            100001.0,
            300003.0,
            400004.0,
            400004.0,
            # validation test
            900009.0,
            900009.0,
            900009.0,
            900009.0,
            900009.0,
        ],
        "Month": [  # object
            f"{datetime.now().month}-{datetime.now().year}",
            f"{datetime.now().month}-{datetime.now().year}",
            f"{datetime.now().month}-{datetime.now().year}",
            f"{datetime.now().month}-{datetime.now().year}",
            f"{datetime.now().month}-{datetime.now().year}",
            f"{datetime.now().month}-{datetime.now().year}",
            datetime(2013, 12, 1).strftime("%m-%Y"),
            # ---
            f"{datetime.now().month}-{datetime.now().year}",
            f"{datetime.now().month}-{datetime.now().year}",
            f"{datetime.now().month}-{datetime.now().year}",
            f"{datetime.now().month}-{datetime.now().year}",
            "abcdef",
        ],
        "LG Code": [  # float64
            111111.0,
            111111.0,
            222222.0,
            222222.0,
            333333.0,
            444444.0,
            444444.0,
            # ---
            999951.0,
            999952.0,
            999953.0,
            999954.0,
            999955.0,
        ],
        "Shipping Plant 1": [  # object
            "R2D2",
            "R2D2",
            "R2D2",
            "R2D2",
            "R2D2",
            "R2D2",
            "R2D2",
            # ---
            "C3PO",
            "R2D2",
            "R2D2",
            "OTHER_PLANT",
            "R2D2",
        ],
        "ratio SP1": [  # object
            "1.0",
            "NaN",
            "0.2",
            "1.0",
            "",
            "0.4",
            "0.7",
            # ---
            "0.4",
            "0.4",
            "0.5",
            "0.4",
            "0.4",
        ],
        "Shipping Plant 2": [  # object
            "C3PO",
            "C3PO",
            "C3PO",
            "C3PO",
            "C3PO",
            "C3PO",
            "C3PO",
            # ---
            "C3PO",
            "C3PO",
            "C3PO",
            "C3PO",
            "C3PO",
        ],
        "ratio SP2": [  # object
            "0",
            "1",
            "0.8",
            "NaN",
            "1",
            "0.6",
            "0.3",
            # ---
            "0.6",
            "abcd",
            "0.6",
            "0.6",
            "0.6",
        ],
    },
}


#   LG Code	Month	    FLOW - ...  LGK	            CustomerGinger Code 17	                m2	        Total m²	Percem²	R2D2	C3PO	Shipping Plant
CHECK_MODIFICATION_THROUGH_CESSIONS = (
    # 0	111111	2023-09-19	1234.123456	123456789012	100001	123456Q99X1111x9999L12345678	16000.00	40000.00	0.4	1   	0   	R2D2    X mod
    {
        "Index": 0,
        "LG Code": 111111,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 100001,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 16000.0,
        "Total m²": 40000.0,
        "Percentage m²": 0.4,
        "R2D2": 1,
        "C3PO": 0,
        "Shipping Plant": "R2D2",
    },
    # 1	111111	2023-09-19	1234.123456	123456789012	500005	123456Q99X1111x9999L12345678	54321.00	54321.00	1   	0.20000	0.80000	R2D2    x remains - undefined customer
    {
        "Index": 1,
        "LG Code": 111111,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 500005,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 54321.0,
        "Total m²": 54321.0,
        "Percentage m²": 1,
        "R2D2": 0.2,
        "C3PO": 0.8,
        "Shipping Plant": "R2D2",
    },
    # 2	111111	2023-09-19	1234.123456	123456789012	100001	123456Q99X1111x9999L12345678	12345.67	12345.67	1   	1   	0   	R2D2    X mod
    {
        "Index": 2,
        "LG Code": 111111,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 100001,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 12345.67,
        "Total m²": 12345.67,
        "Percentage m²": 1,
        "R2D2": 1,
        "C3PO": 0,
        "Shipping Plant": "R2D2",
    },
    # 3	111111	2023-09-19	1234.123456	123456789012	200002	123456Q99X1111x9999L12345678	12345.67	12345.67	1   	0   	1   	C3PO    X mod
    {
        "Index": 3,
        "LG Code": 111111,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 200002,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 12345.67,
        "Total m²": 12345.67,
        "Percentage m²": 1,
        "R2D2": 0,
        "C3PO": 1,
        "Shipping Plant": "C3PO",
    },
    # 4	111111	2023-09-19	1234.123456	123456789012	500005	123456Q99X1111x9999L12345678	12345.67	12345.67	1   	1.00000	0.00000	R2D2    x remains - undefined customer
    {
        "Index": 4,
        "LG Code": 111111,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 500005,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 12345.67,
        "Total m²": 12345.67,
        "Percentage m²": 1,
        "R2D2": 1,
        "C3PO": 0,
        "Shipping Plant": "R2D2",
    },
    # 5	222222	2023-09-19	1234.123456	123456789012	100001	123456Q99X1111x9999L12345678	10000.00	1000.00	    0.1 	1   	0   	R2D2    X mod
    {
        "Index": 5,
        "LG Code": 222222,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 100001,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 10000.0,
        "Total m²": 1000.0,
        "Percentage m²": 0.1,
        "R2D2": 1,
        "C3PO": 0,
        "Shipping Plant": "R2D2",
    },
    # 6	222222	2023-09-19	1234.123456	123456789012	200002	123456Q99X1111x9999L12345678	10000.10	10000.10	1   	1    	0    	R2D2    X mod - and append second row as 16
    {
        "Index": 6,
        "LG Code": 222222,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 200002,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 10000.10,
        "Total m²": 10000.10,
        "Percentage m²": 1,
        "R2D2": 1,
        "C3PO": 0,
        "Shipping Plant": "R2D2",
    },
    # 7	333333	2023-09-19	1234.123456	123456789012	300003	123456Q99X1111x9999L12345678	10000.00	10000.00	1   	0   	1   	C3PO    X mod
    {
        "Index": 7,
        "LG Code": 333333,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 300003,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 10000.0,
        "Total m²": 10000.0,
        "Percentage m²": 1,
        "R2D2": 0,
        "C3PO": 1,
        "Shipping Plant": "C3PO",
    },
    # 8	333333	2023-09-19	1234.123456	123456789012	500005	123456Q99X1111x9999L12345678	20000.00	20000.00	1   	0.20000	0.80000	R2D2    X remains - undefined customer
    {
        "Index": 8,
        "LG Code": 333333,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 500005,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 20000.0,
        "Total m²": 20000.0,
        "Percentage m²": 1,
        "R2D2": 0.2,
        "C3PO": 0.8,
        "Shipping Plant": "R2D2",
    },
    # 9	444444	2023-09-19	1234.123456	123456789012	400004	123456Q99X1111x9999L12345678	12000.00	36000.00	0.33333 	1    	0    	R2D2    X mod - and append second row as 17
    {
        "Index": 9,
        "LG Code": 444444,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 400004,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 12000.0,
        "Total m²": 36000.0,
        "Percentage m²": 0.33333,
        "R2D2": 1,
        "C3PO": 0,
        "Shipping Plant": "R2D2",
    },
    # 10	444444	2013-12-11	1234.123456	123456789012	400004	123456Q99X1111x9999L12345678	28000.00	28000.00	1   	1    	0   	R2D2    X mod - and append second row as 18
    {
        "Index": 10,
        "LG Code": 444444,
        "Month": datetime(2013, 12, 11, 0, 0, 0, 0),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 400004,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 28000.0,
        "Total m²": 28000.0,
        "Percentage m²": 1,
        "R2D2": 1,
        "C3PO": 0,
        "Shipping Plant": "R2D2",
    },
    # 11	999951	2023-09-19	1234.123456	123456789012	900009	123456Q99X1111x9999L12345678	10000.00	10000.00	1   	0.00000	1.00000	C3PO    X remains - same plant on both sides
    {
        "Index": 11,
        "LG Code": 999951,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 900009,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 10000.0,
        "Total m²": 10000.0,
        "Percentage m²": 1,
        "R2D2": 0,
        "C3PO": 1,
        "Shipping Plant": "C3PO",
    },
    # 12	999952	2023-09-19	1234.123456	123456789012	900009	123456Q99X1111x9999L12345678	10000.00	10000.00	1   	0.20000	0.80000	R2D2    X remains - ratio in wrong format
    {
        "Index": 12,
        "LG Code": 999952,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 900009,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 10000.0,
        "Total m²": 10000.0,
        "Percentage m²": 1,
        "R2D2": 0.2,
        "C3PO": 0.8,
        "Shipping Plant": "R2D2",
    },
    # 13	999953	2023-09-19	1234.123456	123456789012	900009	123456Q99X1111x9999L12345678	10000.00	10000.00	1   	0.50000	0.50000	C3PO    X remains - sum of ratio is to much
    {
        "Index": 13,
        "LG Code": 999953,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 900009,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 10000.0,
        "Total m²": 10000.0,
        "Percentage m²": 1,
        "R2D2": 0.5,
        "C3PO": 0.5,
        "Shipping Plant": "C3PO",
    },
    # 14	999954	2023-09-19	1234.123456	123456789012	900009	123456Q99X1111x9999L12345678	10000.00	10000.00	1   	0.80000	0.20000	R2D2    X remains - unknown plant name
    {
        "Index": 14,
        "LG Code": 999954,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 900009,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 10000.0,
        "Total m²": 10000.0,
        "Percentage m²": 1,
        "R2D2": 0.8,
        "C3PO": 0.2,
        "Shipping Plant": "R2D2",
    },
    # 15	999955	2023-09-19	1234.123456	123456789012	900009	123456Q99X1111x9999L12345678	10000.00	10000.00	1   	1.00000	0.00000	R2D2    X remains - Month in wrong format
    {
        "Index": 15,
        "LG Code": 999955,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 900009,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 10000.0,
        "Total m²": 10000.0,
        "Percentage m²": 1,
        "R2D2": 1,
        "C3PO": 0,
        "Shipping Plant": "R2D2",
    },
    # 16	222222	2023-09-19	1234.123456	123456789012	200002	123456Q99X1111x9999L12345678	40000.40	40000.40	1   	0    	1   	C3PO    X add - second part of 6
    {
        "Index": 16,
        "LG Code": 222222,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 200002,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 40000.40,
        "Total m²": 40000.40,
        "Percentage m²": 1,
        "R2D2": 0,
        "C3PO": 1,
        "Shipping Plant": "C3PO",
    },
    # 17	444444	2023-09-19	1234.123456	123456789012	400004	123456Q99X1111x9999L12345678	18000.00	54000.00	0.33333   	0    	1    	C3PO    X add - second part of 9
    {
        "Index": 17,
        "LG Code": 444444,
        "Month": datetime.combine(datetime.now().date(), time(0, 0, 0, 0)),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 400004,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 18000.0,
        "Total m²": 54000.0,
        "Percentage m²": 0.33333,
        "R2D2": 0,
        "C3PO": 1,
        "Shipping Plant": "C3PO",
    },
    # 18	444444	2013-12-11	1234.123456	123456789012	400004	123456Q99X1111x9999L12345678	40000.00	40000.00	1   	0   	1    	C3PO    X add - second part of 10
    {
        "Index": 18,
        "LG Code": 444444,
        "Month": datetime(2013, 12, 11),
        "FLOW - DE - VIEW - Forecast Sales": 1234.123456,
        "LGK": 123456789012,
        "Customer": 400004,
        "Ginger Code 17": "123456Q99X1111x9999L12345678",
        "m2": 12000.0,
        "Total m²": 12000.0,
        "Percentage m²": 1,
        "R2D2": 0,
        "C3PO": 1,
        "Shipping Plant": "C3PO",
    },
)
