from django.conf import settings

from core.models.generics import StampedUUIDModel


# from django.db import models


class OrderBook(StampedUUIDModel):
    # Planned Production Date
    # planned_production_date = models.CharField(max_length=100, blank=True, default="")

    # orderbook["Planned Production Date"] = pd.to_datetime(orderbook["Planned Production Date"], format=_format)
    # orderbook["Planned Production Week"] = orderbook["Planned Production Date"].dt.isocalendar().week
    # orderbook["Planned Production Date"] = orderbook["Planned Production Date"].dt.strftime(_format)
    # orderbook = next_orders.merge(stock_ras, on="Ginger Code 17", how="left")
    # orderbook["cumsum_order"] = orderbook.groupby("Ginger Code 17")["TO"].cumsum()
    # orderbook["Remaining Stock"] = orderbook["to"] - orderbook["cumsum_order"]

    # coating = row["Coating"]
    # tint_thickness = f'{row["Tint"]}{row["Nominal Thickness"]}'
    # expected_loading_date = datetime.strptime(row["Expected Loading Date"], "%d.%m.%Y")
    # quality = row["Quality"]

    # OTIF Predictor (OK, NP, NOK)
    # otif_predictor = models.CharField(max_length=100, blank=True, default="")

    def get_stock_threshold(self) -> float:
        # STOCK_THRESHOLD should be a negative number, that shows how much we can trust
        # the availability of the stock
        # (tonne this order) - (cummulated tonnage in stock) = remaining stock
        # if we have half a tonne left (-500 kg), we can produce
        # STOCK_THRESHOLD: float = -0.5  # 500 kg
        return settings.STOCK_THRESHOLD
