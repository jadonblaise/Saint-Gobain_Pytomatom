import apps.ordermanagement.plans.collections as collections


def test_extract_key_with_production_data(prepared_production_plan_coater):
    """create collection sorted by 'coating'"""
    r = collections.extract_key(
        plan=prepared_production_plan_coater.payload,
        key="coating",
        stringify=False,
    )
    assert r == prepared_production_plan_coater.expected


def test_extract_key_stringify_function_modification(
    fake_plan_key_modification,
):
    """collection keys must be string type"""
    r = collections.extract_key(
        plan=fake_plan_key_modification.payload,
        key="key",
        stringify=True,
    )
    assert r == fake_plan_key_modification.expected


def test_extract_key_stringify_function_no_modification(
    fake_plan_no_key_modification,
):
    """collection keys must be original type"""
    r = collections.extract_key(
        plan=fake_plan_no_key_modification.payload,
        key="key",
        stringify=False,
    )
    assert r == fake_plan_no_key_modification.expected


def test_extract_key_key_error(prepared_production_plan_coater):
    """no error should be happend with wrong key"""
    collections.extract_key(
        plan=prepared_production_plan_coater.payload,
        key="unknown",
        stringify=False,
    )


def test_deep_extract(prepared_production_plan_float):
    """add another level to collection sorted by 'thickness'"""
    r = collections.deep_extract(
        plan=prepared_production_plan_float.payload,
        key="thickness",
        stringify=True,
    )
    assert r == prepared_production_plan_float.expected
