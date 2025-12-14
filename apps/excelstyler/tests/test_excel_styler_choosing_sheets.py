import re

import pytest

from apps.excelstyler.exceptions import ExcelSheetNotFound
from apps.excelstyler.styler import ExcelSheetStyler


"""checks definition of sheet to work on"""


def test_choose_first_sheet(excelbuffer, mapping_sheet_one, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=1)
    assert styler.mapping == mapping_sheet_one


def test_choose_second_sheet(excelbuffer, mapping_sheet_two, name_sheet_2):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_2, count_of_header_rows=1)
    assert styler.mapping == mapping_sheet_two


def test_choose_third_sheet(excelbuffer, mapping_sheet_three, name_sheet_3):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_3, count_of_header_rows=1)
    assert styler.mapping == mapping_sheet_three


def test_choose_unknown_sheet(excelbuffer):
    with pytest.raises(
        ExcelSheetNotFound,
        match=re.escape(
            r"Could not find sheet in passed Excel file. exc=KeyError('Worksheet WrongName does not exist.')"
        ),
    ):
        ExcelSheetStyler(buffer=excelbuffer, sheet_name="WrongName")
