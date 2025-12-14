import io
from io import BytesIO
from typing import Any

import pandas as pd
from openpyxl import Workbook

from django.conf import settings


def to_xlsx(*, df: pd.DataFrame, filename: str, sheet_name: str, buffer: bool = False) -> Any | io.BytesIO:
    """
    Export df to xlsx file or xlsx buffer
    """
    file_or_buffer = settings.ROOT_DIR / "outputs" / filename if not buffer else io.BytesIO()
    df.to_excel(file_or_buffer, sheet_name=sheet_name, index=False)
    return file_or_buffer


def openpyxl_to_disk(*, workbook: Workbook, filename: str, buffer: bool = False) -> Any | io.BytesIO:
    file_or_buffer = settings.ROOT_DIR / "outputs" / filename if not buffer else BytesIO()
    workbook.save(file_or_buffer)
    return file_or_buffer
