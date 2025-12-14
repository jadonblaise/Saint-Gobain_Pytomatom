import pytest

from apps.datalake.imports import transform_product
from apps.datalake.models import SAPProduct

from ..factories.products import product_factory


@pytest.fixture
def raw_product_legacy():
    yield {
        "c_divi": "G035",
        "ginger_code_17": "101464Q22T2250x3210T80080010",
        "c_article": "000000001014640060",
        "l_article": "55.2P            LA8008INS3210*2250L0T00",
        "typ_appro": "X",
        "service_chart": "Out",
        "dzeit": "0.0",
        "stksecumin": 0.0,
        "ginger_meins": "PIL",
        "havp": "CLASSICS",
        "c_embl": "002",
        "lembl": "INSTILLG",
        "lib_com": "SGG STADIP PROTECT 211 (55.2P) OPALE",
        "lg_short_description": "55.2P",
        "lg_long_description": None,
        "c_article_lg": "101464",
        "lfam": None,
        "lsfam": "BI STADIP",
        "lcoat": "NONE",
        "limpr": "NONE",
        "ltein": "CLEAR",
        "c_qual": "22",
        "ltrai": "NONE",
        "epaisn": "1076",
        "lqual": "LAMINA",
        "ltmes": "DLF",
        "dimension": "2250 x 3210",
        "lon": "03210",
        "lar": "02250",
        "c_pile": "8008",
        "pack_family": "UEB",
        "lstri": "TRANS",
        "c_marq": "0",
        "c_intp": "0",
        "lintv": "LUC",
        "safety_time": 0.0,
        "safety_stock_unit": " ",
        "safety_stock_quantity": None,
        "lead_time": 0.0,
        "servlt": 0.0,
        "cut_pmm_plf": 4500.0,
        "size_t_mm": 3210,
        "nbvol_pack": 8,
    }


@pytest.fixture
def raw_product():
    yield {
        "c_divi": "G035",
        "gingerCode17": "100064Q06X3210x5000L40040012",
        "c_article": "000000001000640713",
        "l_article": "DIAMANT 10MM    BK4004INS15000*3210L2L00",
        "typAppro": "X",
        "serviceChart": "MTO",
        "dzeit": "0.0",
        "stkSecuMin": 0.0,
        "gingerMeins": "PIL",
        "havp": "HAVP",
        "c_embl": "002",
        "lembl": "INSTILLG",
        "libCom": "SGG DIAMANT 10 MM",
        "lgShortDescription": "DIAMANT 10MM",
        "lgLongDescription": None,
        "c_article_lg": "100064",
        "lfam": None,
        "lsfam": "DIAMANT",
        "lcoat": "NONE",
        "limpr": "NONE",
        "ltein": "EXTRACL",
        "c_qual": "06",
        "ltrai": "NONE",
        "epaisn": "1000",
        "lqual": "BLDSKN",
        "ltmes": "XXL",
        "dimension": "3210 x 15000",
        "lon": "15000",
        "lar": "03210",
        "c_pile": "4004",
        "packFamily": "5,8T",
        "lstri": "LONGI",
        "c_marq": "0",
        "c_intp": "2",
        "lintv": "LUC",
        "safetyTime": 0.0,
        "safetyStockUnit": " ",
        "safetyStockQuantity": None,
        "leadTime": 91.0,
        "servlt": 91.0,
        "cutPmmPlf": 0.0,
        "sizeTMm": 3210,
        "nbVolPack": 4,
    }


@pytest.fixture
def product(raw_product):
    """
    Yields from product factory.
    """
    _product = transform_product(raw_product)
    product = product_factory(**_product)
    yield product
    SAPProduct.objects.get(sap_article_number=product.sap_article_number).delete()  # type: ignore[no-untyped-call]
