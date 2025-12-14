from datetime import datetime

from apps.datalake.models import SAPOrder


def get_last_datalake_update_date() -> datetime | None:
    """Get the last update date of the datalake saporders."""
    lastorder = SAPOrder.objects.order_by("-lastmodified_at").first()
    if lastorder is None:
        return None
    return lastorder.lastmodified_at
