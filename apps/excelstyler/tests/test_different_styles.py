"""Applying different styles to the same sheet without errors."""


def test_style(styler):
    """able to run without errors"""
    collection = [
        styler.Definition(column="__Special__"),
        styler.Definition(column="____"),
        styler.Definition(column="__Cases__"),
        styler.Definition(column="__Double__", formula='__Double__="D"', fill_color_hex="abc785"),
        styler.Definition(column="__Col E__", formula='__Col E__="J"', fill_color_hex="abc785"),
        styler.Definition(column="__Col F__", formula='__Col F__="A"', fill_color_hex="abc785"),
    ]
    styler.apply_conditional_collection(style_collection=collection)
