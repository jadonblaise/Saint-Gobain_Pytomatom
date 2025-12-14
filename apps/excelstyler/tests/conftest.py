from io import BytesIO
from pathlib import Path

import pytest

from django.conf import settings

from apps.excelstyler.styler import ExcelSheetStyler


def load_file(path: Path):
    with open(path, "rb") as excel_file:
        return excel_file.read()

@pytest.fixture
def name_sheet_1():
    yield "SheetOne"


@pytest.fixture
def name_sheet_2():
    yield "SheetTwo"


@pytest.fixture
def name_sheet_3():
    yield "SheetThree"


@pytest.fixture
def name_column_1():
    yield "Column One"


@pytest.fixture
def name_column_2():
    yield "Column Two"


@pytest.fixture
def name_column_3():
    yield "Column Three"


@pytest.fixture
def mapping_sheet_one(name_column_1, name_column_2, name_column_3):
    yield {name_column_1: "A", name_column_2: "B", name_column_3: "C"}


@pytest.fixture
def mapping_sheet_two():
    yield {"One": "A", "Two": "B", "Three": "C"}


@pytest.fixture
def mapping_sheet_three():
    yield {
        "Special": "A",
        "Cases": "C",
        "Double": "G",
        "Col E": "E",
        "Col F": "F",
        "Col H": "H",
        "Col I": "I",
    }


@pytest.fixture
def wrong_filebuffer():
    """
    Could be done with some simple parametrized fuzzing against non-excel files.
    """
    yield BytesIO(load_file(path=settings.ROOT_DIR / "test" / "files" / "excelstyler" / "sample.txt"))


@pytest.fixture
def excelbuffer():
    """For convenience just 'assumes' correct excel buffer is used."""
    yield BytesIO(load_file(path=settings.ROOT_DIR / "test" / "files" / "excelstyler" / "sample.xlsx"))


@pytest.fixture
def styler(excelbuffer, name_sheet_1):
    """This yields an opinionated styler with default settings."""
    yield ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=1)
