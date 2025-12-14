import io
from pathlib import Path

import pandas as pd

from django.conf import settings


def as_df(
    *,
    path: Path | None = None,
    sheet_name: str | None = None,
    divergent_header: int | None = None,
    usecols: list | None = None,
    buffer: io.BytesIO | None = None,
    as_csv: bool = False,
    seperator=";",
) -> pd.DataFrame:
    """
    Read files from disk and import to dataframe
    """
    if path is None and buffer is None:
        raise ValueError("Either path or buffer must be provided.")
    if path is not None and buffer is not None:
        raise ValueError("Either path or buffer must be provided, not both.")

    path_or_buffer = settings.ROOT_DIR / path if buffer is None else buffer  # type: ignore[operator]

    kwargs = {}
    if sheet_name is not None:
        kwargs["sheet_name"] = sheet_name
    if divergent_header is not None:
        kwargs["header"] = divergent_header  # type: ignore[assignment]
    if usecols is not None:
        kwargs["usecols"] = usecols  # type: ignore[assignment]

    resource = (
        pd.read_excel(path_or_buffer, **kwargs) if not as_csv else pd.read_csv(path_or_buffer, sep=seperator, **kwargs)
    )

    return resource
