import pytest

from apps.orderbooks.atom import predict_orders, Orders


@pytest.mark.slow
def test_order_prediction_from_excel(
    new_orders_orderbook,
    old_orders_orderbook,
    orion_raw,
    article_ginger,
    float_plan,
    coater_plan,
):
    orders = Orders(
        new_orders=new_orders_orderbook,
        old_orders=old_orders_orderbook,
        orion_raw=orion_raw,
        article_ginger=article_ginger,
        float_plan=float_plan,
        coater_plan=coater_plan,
    )
    df = predict_orders(
        orders=orders,
    )

    assert df is not None
