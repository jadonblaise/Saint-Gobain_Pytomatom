"""checks different variations of column letters"""


def test_single_style_default_with_column_letter_a_validation(styler):
    style = styler.Definition(column="A")
    column_validation = styler._column_letter_is_valid(style=style)
    assert column_validation is True


def test_single_style_default_with_column_letter_a_recognition(styler, name_column_1):
    column_recognition = styler._get_column_letter(column_name=f"__{name_column_1}__")
    assert column_recognition == "A"


def test_single_style_default_with_column_letter_b_validation(styler):
    style = styler.Definition(column="B")
    column_validation = styler._column_letter_is_valid(style=style)
    assert column_validation is True


def test_single_style_default_with_column_letter_b_recognition(styler, name_column_2):
    column_recognition = styler._get_column_letter(column_name=f"__{name_column_2}__")
    assert column_recognition == "B"


def test_single_style_default_with_column_name_a_validation(styler, name_column_1):
    style = styler.Definition(column=f"__{name_column_1}__")
    column_validation = styler._column_letter_is_valid(style=style)
    assert column_validation is True


def test_single_style_default_with_column_name_a_recognition(styler, name_column_1):
    column_recognition = styler._get_column_letter(column_name=f"__{name_column_1}__")
    assert column_recognition == "A"


def test_single_style_default_with_column_name_b_validation(styler, name_column_1):
    style = styler.Definition(column=f"__{name_column_1}__")
    column_validation = styler._column_letter_is_valid(style=style)
    assert column_validation is True


def test_single_style_default_with_column_name_b_recognition(styler, name_column_2):
    column_recognition = styler._get_column_letter(column_name=f"__{name_column_2}__")
    assert column_recognition == "B"


def test_single_style_default_in_wrong_format_1_validation(styler):
    style = styler.Definition(column="__unknown__")
    column_validation = styler._column_letter_is_valid(style=style)
    assert column_validation is False


def test_single_style_default_in_wrong_format_2_validation(styler):
    # column ZZZ seems to be reachable (made tests)
    style = styler.Definition(column="AAAA")
    column_validation = styler._column_letter_is_valid(style=style)
    assert column_validation is False


def test_single_style_default_in_wrong_format_3_validation(styler):
    style = styler.Definition(column="__unknown__")
    styling_result = styler.apply_conditional(style=style)
    assert styling_result is False


def test_single_style_default_in_wrong_format_4_validation(styler):
    style = styler.Definition(column="AAAA")
    styling_result = styler.apply_conditional(style=style)
    assert styling_result is False
