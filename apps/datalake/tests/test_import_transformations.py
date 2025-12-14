import pytest

from apps.datalake.imports import transform_product, DataValidationError
from apps.datalake.models import Plant


# from test.classes import ExpectedClosureContract


@pytest.mark.django_db
def test_product_transformation(raw_product, product):
    _product = transform_product(raw_product)
    assert _product["sap_article_number"] == product.sap_article_number


@pytest.mark.django_db
def test_raw_product_plant_is_plant_instance(raw_product):
    transformed = transform_product(raw_product)
    assert isinstance(transformed["plant"], Plant)


@pytest.mark.django_db
def test_missing_keys_raise_datavalidation_errors():
    with pytest.raises(
        DataValidationError, match=r"^Failed to transform product, missing key 'c_divi' \(plant division id\).$"
    ):
        _ = transform_product(
            {
                "foo": "bar",
            }
        )
    with pytest.raises(
        DataValidationError, match=r"^Failed to transform product, missing key 'c_article' \(SAP-article-number\).$"
    ):
        _ = transform_product(
            {
                "c_divi": "dummy-division",
            }
        )


@pytest.mark.django_db
def test_existent_keys_do_not_raise():
    transformed = transform_product(
        {
            "c_divi": "dummy-division",
            "c_article": "dummy-sap-article",
        }
    )
    assert transformed["plant"] == Plant.objects.get(division="dummy-division")


@pytest.mark.django_db
def test_raw_products_transform_without_errors_for_all_initial_data(initial_raw_product_txt):
    _ = transform_product(initial_raw_product_txt)


# @pytest.mark.parametrize(
#     "contract",
#     [
#         ExpectedClosureContract(kwargs={"key_candidate": "c_divi"}, expected=True),
#         ExpectedClosureContract(kwargs={"key_candidate": ""}, expected=False),
#         ExpectedClosureContract(kwargs={"key_candidate": 0}, expected=False),
#         ExpectedClosureContract(kwargs={"key_candidate": False}, expected=False),
#         ExpectedClosureContract(kwargs={"key_candidate": True}, expected=False),
#     ],
# )
# def test_is_valid_primary_key(contract):
#     assert contract.expected == is_valid_primary_key(**contract.kwargs)


# TODO : Write test for transformation of Purchase, Stock, SAPOrder Management
