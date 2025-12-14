import json
from pathlib import Path

import pytest

from core.inout.files import read_from_disk
from test.fixtures.datalake import raw_product, product  # noqa: F401


parent = Path(__file__).parent.parent.parent.parent


products = json.loads(read_from_disk(parent / "resources/datalake/json_products.txt"))["products"]


@pytest.fixture(params=products)
def initial_raw_product_txt(request):
    yield request.param
