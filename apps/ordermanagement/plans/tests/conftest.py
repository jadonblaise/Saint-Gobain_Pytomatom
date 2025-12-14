import datetime
from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class TestInput:
    payload: Any
    expected: Any


@pytest.fixture
def prepared_production_plan_coater():
    """small coater production plan"""
    payload = [
        {"date": datetime.date(2021, 1, 2), "coating": "W", "available": 0.0},
        {"date": datetime.date(2021, 1, 3), "coating": "PLT XN", "available": 38269.75714383185},
        {"date": datetime.date(2021, 1, 4), "coating": "PLT XN", "available": 42919.35380616656},
        {"date": datetime.date(2021, 1, 5), "coating": "PLT XNII", "available": 22220.983707552332},
        {"date": datetime.date(2021, 1, 6), "coating": "PLT XNII", "available": 35553.57393208373},
        {"date": datetime.date(2021, 1, 7), "coating": "ECLAZ", "available": 27720.0},
        {"date": datetime.date(2021, 1, 8), "coating": "ECLAZ", "available": 36960.0},
        {"date": datetime.date(2021, 1, 9), "coating": "ECLAZ", "available": 36960.0},
        {"date": datetime.date(2021, 1, 10), "coating": "ECLAZ", "available": 36960.0},
        {"date": datetime.date(2021, 1, 11), "coating": "ECLAZ", "available": 36960.0},
        {"date": datetime.date(2021, 1, 12), "coating": "ECLAZ", "available": 36960.0},
    ]
    expected = {
        "W": [
            {"date": datetime.date(2021, 1, 2), "coating": "W", "available": 0.0},
        ],
        "PLT XN": [
            {"date": datetime.date(2021, 1, 3), "coating": "PLT XN", "available": 38269.75714383185},
            {"date": datetime.date(2021, 1, 4), "coating": "PLT XN", "available": 42919.35380616656},
        ],
        "PLT XNII": [
            {"date": datetime.date(2021, 1, 5), "coating": "PLT XNII", "available": 22220.983707552332},
            {"date": datetime.date(2021, 1, 6), "coating": "PLT XNII", "available": 35553.57393208373},
        ],
        "ECLAZ": [
            {"date": datetime.date(2021, 1, 7), "coating": "ECLAZ", "available": 27720.0},
            {"date": datetime.date(2021, 1, 8), "coating": "ECLAZ", "available": 36960.0},
            {"date": datetime.date(2021, 1, 9), "coating": "ECLAZ", "available": 36960.0},
            {"date": datetime.date(2021, 1, 10), "coating": "ECLAZ", "available": 36960.0},
            {"date": datetime.date(2021, 1, 11), "coating": "ECLAZ", "available": 36960.0},
            {"date": datetime.date(2021, 1, 12), "coating": "ECLAZ", "available": 36960.0},
        ],
    }
    yield TestInput(payload=payload, expected=expected)


@pytest.fixture
def fake_plan_payload():
    payload = [
        {"date": datetime.date(2021, 1, 2), "key": 42, "available": 1.23},
        {"date": datetime.date(2022, 3, 4), "key": 42, "available": 4.56},
        {"date": datetime.date(2021, 1, 3), "key": 42.4, "available": 1.23},
        {"date": datetime.date(2022, 3, 4), "key": 42.4, "available": 4.56},
    ]
    yield payload


@pytest.fixture
def fake_plan_key_modification(fake_plan_payload):
    """stringify function - modification to string"""
    expected = {
        "42": [
            {"date": datetime.date(2021, 1, 2), "key": 42, "available": 1.23},
            {"date": datetime.date(2022, 3, 4), "key": 42, "available": 4.56},
        ],
        "42.4": [
            {"date": datetime.date(2021, 1, 3), "key": 42.4, "available": 1.23},
            {"date": datetime.date(2022, 3, 4), "key": 42.4, "available": 4.56},
        ],
    }
    yield TestInput(payload=fake_plan_payload, expected=expected)


@pytest.fixture
def fake_plan_no_key_modification(fake_plan_payload):
    """stringify function - no modification"""
    expected = {
        42: [
            {"date": datetime.date(2021, 1, 2), "key": 42, "available": 1.23},
            {"date": datetime.date(2022, 3, 4), "key": 42, "available": 4.56},
        ],
        42.4: [
            {"date": datetime.date(2021, 1, 3), "key": 42.4, "available": 1.23},
            {"date": datetime.date(2022, 3, 4), "key": 42.4, "available": 4.56},
        ],
    }
    yield TestInput(payload=fake_plan_payload, expected=expected)


@pytest.fixture
def prepared_production_plan_float():
    """small float production plan"""
    payload = {
        "PLC": [
            {"date": datetime.date(2024, 1, 15), "tint": "PLC", "thickness": 3.9, "available": 680},
            {"date": datetime.date(2024, 1, 16), "tint": "PLC", "thickness": 3.9, "available": 680},
            {"date": datetime.date(2024, 1, 17), "tint": "PLC", "thickness": 4.9, "available": 680},
        ],
        "Diamant": [
            {"date": datetime.date(2024, 5, 17), "tint": "Diamant", "thickness": 4.9, "available": 680},
            {"date": datetime.date(2024, 5, 18), "tint": "Diamant", "thickness": 5.9, "available": 680},
            {"date": datetime.date(2024, 5, 19), "tint": "Diamant", "thickness": 5.9, "available": 680},
        ],
    }
    expected = {
        "PLC": {
            "3.9": [
                {"date": datetime.date(2024, 1, 15), "tint": "PLC", "thickness": 3.9, "available": 680},
                {"date": datetime.date(2024, 1, 16), "tint": "PLC", "thickness": 3.9, "available": 680},
            ],
            "4.9": [
                {"date": datetime.date(2024, 1, 17), "tint": "PLC", "thickness": 4.9, "available": 680},
            ],
        },
        "Diamant": {
            "4.9": [
                {"date": datetime.date(2024, 5, 17), "tint": "Diamant", "thickness": 4.9, "available": 680},
            ],
            "5.9": [
                {"date": datetime.date(2024, 5, 18), "tint": "Diamant", "thickness": 5.9, "available": 680},
                {"date": datetime.date(2024, 5, 19), "tint": "Diamant", "thickness": 5.9, "available": 680},
            ],
        },
    }
    yield TestInput(payload=payload, expected=expected)
