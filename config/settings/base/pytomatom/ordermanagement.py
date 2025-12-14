from decimal import Decimal

from apps.orderbooks.references import PlantProductionReference

# STOCK_THRESHOLD should be a negative number, that shows how much we can trust
# the availability of the stock
# (tonne this order) - (cumulated tonnage in stock) = remaining stock
# if we have half a tonne left (-500 kg), we can produce
STOCK_THRESHOLD: float = -0.5  # 500 kg
# That should probably be a just a positive number...
STOCK_TONS_THRESHOLD: Decimal = Decimal(STOCK_THRESHOLD * -1)  # 500 kg
assert STOCK_TONS_THRESHOLD >= 0, "STOCK_TONS_THRESHOLD should be a positive number"

OM_SHEET_NAME = "Ordermanagement"

REACTION_TIME_LAMINATED_GLASS = 3  # in days

STOCK_DECIMAL_PLACES = Decimal(10) ** -3  # A.F said: round tons to 3 decimal places (full kg)
LAMINATED_SAFETY_GLASS_QUALITY: int = 22

PLANT: dict = {
    "PRODUCT_FAMILIES": {
        "FLOAT": {  # 'normales' Flachglas
            "DIAMANT": {  # sub family
                "tint": "EXTRACLEAR",  # color
                "thickness": range(210, 1900),  # in mm
                "coating": None,
                "production_on": "Float",
                "alternate_name": "DIAMANT",
            },
            "PLANILUX": {  # sub family
                "tint": "CLEAR",
                "thickness": range(210, 1900),  # in mm  # todo: values are not correct - 2.1mm til 19mm...
                "coating": None,
                "production_on": "Float",
                "alternate_name": "PLC",  # todo: check correctness...
            },
        },
        "VSG": {  # Verbundsicherheitsglas
            "BI STADIP": {  # laminated glass
                "production_on": "lamination",
                "alternate_name": None,
            },
            "STD SILENCE": {
                "production_on": "lamination",
                "alternate_name": None,
            },
        },
        # hint: WÄRMESCHUTZGLAS is family 
        # TBD: (category or product ???),
        # hint: ECLAZ (e.g.) is subfamily 
        # TBD: (product, system or system variant ???),
        # TBD: ECLAZ ONE (e.g.) is variant of ECLAZ or on the same layer as ECLAZ ???
        "WÄRMESCHUTZGLAS": {  # wärmeschutz-beschichtetes Glas (am coater produziert)
            "ECLAZ": {
                "production_on": "coater/magnetron",
                "standing_time": 48,  # in hours
                "coating": ["ECLAZ", "ECLAZ ONE"],
            },
            "PLANITHERM": {
                "production_on": "coater/magnetron",
                "standing_time": 0,  # in hours
                "coating": ["PLT XN", "PLT ONE"],
            },
            "TIMELESS": {
                "production_on": "coater/magnetron",
                "standing_time": 24,  # in hours
                "coating": ["TIMELESS", "TMLESS"],
            },
            "BIOCLEAN": {
                "production_on": "coater/magnetron",
                "standing_time": 24,  # in hours
                "coating": ["BIOCLEAN"],
            },
        },
    },
}

PLANT_PRODUCTION_REFERENCE = PlantProductionReference(plant=PLANT)

EXTERNAL_OM_API_ACCESS_TOKEN = "from-sg.digital-with-love"
EXTERNAL_OM_API_DIVISIONS = ["G035"]

# SAPOrders and Stock (GlassPanes) will be deactviated on a new imported chunk
# (from the datalake), if older than this value.
DATALAKE_DEACTIVATION_TIMEOUT = 1  # in hours
