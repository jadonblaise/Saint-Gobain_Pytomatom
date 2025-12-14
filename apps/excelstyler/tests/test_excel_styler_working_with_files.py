import re

import pytest

from apps.excelstyler.exceptions import ExcelFileFormatWrong
from apps.excelstyler.styler import ExcelSheetStyler


"""Check file formats."""


def test_file_is_wrong_format(wrong_filebuffer):
    with pytest.raises(
        ExcelFileFormatWrong, match=re.escape(r"Could not read file. exc=BadZipFile('File is not a zip file')")
    ):
        ExcelSheetStyler(buffer=wrong_filebuffer, sheet_name="unknown")


def test_right_file_format_and_right_sheet_name(excelbuffer, name_sheet_1, mapping_sheet_one):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1)
    assert styler.mapping == mapping_sheet_one
