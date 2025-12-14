from apps.excelstyler.styler import ExcelSheetStyler


"""checks different values to define first row to style"""


def test_default_settings(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1)
    assert styler.first_row_of_content == 2


def test_more_header_rows_settings_border(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=1)
    assert styler.first_row_of_content == 2


def test_zero_header_rows_settings_border(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=0)
    # mapping is still part even in this case
    assert styler.first_row_of_content == 1


def test_wrong_header_rows_settings_border(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=-1)
    assert styler.first_row_of_content == 2


def test_more_header_rows_settings_lil_bit_more(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=2)
    assert styler.first_row_of_content == 3


def test_more_header_rows_settings_lot_more(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=100)
    assert styler.first_row_of_content == 101


def test_more_header_rows_settings_extremely_more(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=2_000_000)
    assert styler.first_row_of_content == 2


def test_wrong_header_rows_settings_lil_bit_lesser(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=-2)
    assert styler.first_row_of_content == 2


def test_wrong_header_rows_settings_lot_lesser(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=-100)
    assert styler.first_row_of_content == 2


def test_wrong_header_rows_settings_extremely_lesser(excelbuffer, name_sheet_1):
    styler = ExcelSheetStyler(buffer=excelbuffer, sheet_name=name_sheet_1, count_of_header_rows=-2_000_000)
    assert styler.first_row_of_content == 2
