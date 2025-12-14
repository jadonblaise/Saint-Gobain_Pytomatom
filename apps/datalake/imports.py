import logging

from .models import GlassPane, Plant, Purchase, SAPOrder, SAPProduct


log = logging.getLogger("django.datalake")


class DataValidationError(Exception):
    pass


def update_or_create_product(raw_product: dict) -> SAPProduct:
    p: dict = transform_product(raw=raw_product)
    try:
        product = SAPProduct.objects.get(sap_article_number=p["sap_article_number"])
    except SAPProduct.DoesNotExist:
        log.debug(f"Creating new product {p['sap_article_number']}")
        return SAPProduct.objects.create(**p)
    for key, value in p.items():
        setattr(product, key, value)
    log.debug(f"Updating product {p['sap_article_number']}")
    product.save()
    return product


def update_or_create_pane(raw_stock: dict) -> GlassPane:
    s: dict = transform_stock(raw=raw_stock)
    try:
        stock = GlassPane.objects.get(sheet_id=s["sheet_id"])
    except GlassPane.DoesNotExist:
        log.debug(f"Creating new stock {s['sheet_id']}")
        return GlassPane.objects.create(**s)
    for key, value in s.items():
        setattr(stock, key, value)
    log.debug(f"Updating stock {s['sheet_id']}")
    stock.active = True
    stock.save()
    return stock


def update_or_create_purchase(raw_purchase: dict) -> Purchase:
    p: dict = transform_purchase(raw=raw_purchase)
    try:
        purchase = Purchase.objects.get(purchase_order_no=p["purchase_order_no"], ginger_code_17=p["ginger_code_17"])
    except Purchase.DoesNotExist:
        log.debug(f"Creating new purchase {p['purchase_order_no']} {p['ginger_code_17']}")
        return Purchase.objects.create(**p)
    for key, value in p.items():
        setattr(purchase, key, value)
    log.debug(f"Updating purchase {p['purchase_order_no']} {p['ginger_code_17']}")
    purchase.save()
    return purchase


def update_or_create_order_management(raw_order_management: dict) -> SAPOrder:
    om: dict = transform_order_management(raw=raw_order_management)
    try:
        order_management = SAPOrder.objects.get(sales_order=om["sales_order"], ginger_code_17=om["ginger_code_17"])
    except SAPOrder.DoesNotExist:
        log.debug(f"Creating new order_management {om['sales_order']} {om['ginger_code_17']}")
        return SAPOrder.objects.create(**om)
    for key, value in om.items():
        setattr(order_management, key, value)
    log.debug(f"Updating order_management {om['sales_order']} {om['ginger_code_17']}")
    order_management.active = True
    order_management.save()
    return order_management


def transform_product(raw: dict) -> dict:
    """
    c_   code : numerique
    l_   libre: long, str or description

    """
    try:
        plant_id = raw["c_divi"]
        # "G035"
    except KeyError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError("Failed to transform product, missing key 'c_divi' (plant division id).")
    plant, _ = Plant.objects.get_or_create(division=plant_id)

    try:
        sap_article_number = raw["c_article"]
        # ! leading zeros
    except KeyError as key:
        log.warning(f"DataValidationError {key=}|{raw=}")
        raise DataValidationError("Failed to transform product, missing key 'c_article' (SAP-article-number).")
    try:
        assert sap_article_number, "sap_article_number must not be empty"
    except AssertionError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError("Failed to transform product, 'c_article' (SAP-article-number) is empty.")

    try:
        product = {
            "plant": plant,
            "sap_article_number": sap_article_number,
            "ginger_code_17": raw.get("gingerCode17", ""),
            # "100064Q06X3210x5000L40040012"
            "sap_technical_description": raw.get("l_article", ""),
            # "DIAMANT 10MM    BK4004INS15000*3210L2L00"
            "procurement_id": raw.get("typAppro", ""),
            # "X", "F"
            "service_level": raw.get("serviceChart", ""),
            # "MTO", "MTS", "Out"
            "delivery_time": float(raw["dzeit"]) if raw.get("dzeit") not in [None, ""] else None,
            # "0.0"  <-- is string in source
            "safety_stock": float(raw["stkSecuMin"]) if raw.get("stkSecuMin") not in [None, ""] else None,
            # 0.0   <--  is float in source
            "safety_stock_unit": raw.get("gingerMeins", ""),
            # "PIL", "PCK"
            "value_category": raw.get("havp", ""),
            # "CLASSICS", "HAVP"
            "emballage": raw.get("c_embl", ""),
            # "002", "026", "027"
            "emballage_description": raw.get("lembl", ""),
            # "LOONRACK", "INSTILLG"
            "commercial_name": raw.get("libCom", ""),
            # "SGG PLANICLEAR 3 MM", "SGG PLANICLEAR 8 MM"
            "family_description_short": raw.get("lgShortDescription", ""),
            # "SKN165IIEP 10 M", "DIAMANT 10MM"
            "family_description_long": raw.get("lgLongDescription", ""),
            # null
            "family_description_code": raw.get("c_article_lg", ""),
            # "104563", "100063", "108607"
            #   <--  part in ginger17
            "family": raw.get("lfam", ""),
            # null
            "sub_family": raw.get("lsfam", ""),
            # "VENUS", "FLOAT ACID", "PLANITHERM"
            "coating": raw.get("lcoat", ""),
            # "PLT XNII", "NONE"
            # <--  NONE is string
            # ! --> is also "NONE" in DB
            "impression": raw.get("limpr", ""),
            # "NONE"  <--  NONE is string
            # ! --> is also "NONE" in DB
            "tint": raw.get("ltein", ""),
            # "CLEAR", "EXTRACL", "GREY"
            "quality": raw.get("c_qual", ""),
            # "04", "27", "02", "06"
            "treatment": raw.get("ltrai", ""),
            # "EASYP", "YES", "NONE"
            # <--  NONE is string
            # ! is also "NONE" in DB,.
            "thickness": raw.get("epaisn", ""),
            # "0800", "1000", "0876"
            "quality_name": raw.get("lqual", ""),
            # "LAMINA", "PLANIT", "BLDSIV"
            "dimension_description": raw.get("ltmes", ""),
            # "DLF", "PLF",
            "dimension": raw.get("dimension", ""),
            # "3210 x 6100", "2250 x 3210", "3210 x 5100"
            # <-- part in ginger17 without empty spaces
            "length": raw.get("lon", ""),
            # "06100", "03210", "05100"
            "width": raw.get("lar", ""),
            # "03210", "02250", "03210"
            "package_type_code": raw.get("c_pile", ""),
            # "8015", "1021", "2080"
            # <-- part in ginger17
            "package_type_family": raw.get("packFamily", ""),
            # "11,5T", "2,8T", "5,8T"
            "orientation": raw.get("lstri", ""),
            # "LONGI", "TRANS"
            # <-- part in ginger17 as "U","L" or "T","T"
            "error_marker": raw.get("c_marq", ""),
            # "0"
            # <-- is string in source
            "inter_product_layer": raw.get("c_intp", ""),
            # "0", "2"
            # <-- is string in source
            "interleaf_description": raw.get("lintv", ""),
            # "LUC", "SPE"
            "safety_stock_time": float(raw["safetyTime"]) if raw.get("safetyTime") not in [None, ""] else None,
            # 0.0, 40.0, 47.0, null
            # ! float and null mixed in source / also in DB.
            "safety_stock_internal_unit": raw.get("safetyStockUnit", "").strip(" ")
            if raw.get("safetyStockUnit") is not None
            else None,
            # " "
            "safety_stock_quantity": float(raw["safetyStockQuantity"])
            if raw.get("safetyStockQuantity") not in [None, ""]
            else None,
            # null
            "lead_time": float(raw["leadTime"]) if raw.get("leadTime") not in [None, ""] else None,
            # 0.0, 43.0
            # <-- float in source
            "lead_time_for_service": float(raw["servlt"]) if raw.get("servlt") not in [None, ""] else None,
            # 0.0, 43.0
            # <-- float in source
            "pre_product_length": float(raw["cutPmmPlf"]) if raw.get("cutPmmPlf") not in [None, ""] else None,
            # 5100.0, 4500.0
            # <-- float
            "pre_product_width": float(raw["sizeTMm"]) if raw.get("sizeTMm") not in [None, ""] else None,
            # 3210, 3225
            # <-- is int in source
            # ! is int in source / is float type in DB.
            "count_of_glass_in_package": int(float(raw["nbVolPack"]))
            if raw.get("nbVolPack") not in [None, ""]
            else None,
            # 8, 7, 20, 61
            # <-- is int in source
        }
    except KeyError as key:
        log.warning(f"DataValidationError {key=}|{raw=}")
        raise DataValidationError(f"Failed to transform product, missing key={key}.")
    except ValueError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError(f"Failed to transform product, invalid value={e}.")
    return {attr: value for attr, value in product.items() if value is not None}


def transform_stock(raw: dict) -> dict:
    try:
        plant_id = raw["origin"]
        # "G035"
    except KeyError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError("Failed to transform product, missing key 'origin' (plant division id).")
    plant, _ = Plant.objects.get_or_create(division=plant_id)

    try:
        sheet_id = raw["idSheet"]
        # "07F0638489"
    except KeyError as key:
        log.warning(f"DataValidationError {key=}|{raw=}")
        raise DataValidationError("Failed to transform stock, missing key 'idSheet' (GBS - Glass Pane Number).")
    try:
        assert sheet_id, "idSheet must not be empty"
    except AssertionError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError("Failed to transform stock, key 'idSheet' (GBS - Glass Pane Number) is empty.")

    try:
        stock = {
            "plant": plant,
            "sheet_id": sheet_id,
            "sap_material": raw.get("material", ""),
            # "1000630277"
            # ! without leading zeros
            "sap_technical_description": raw.get("l_article", ""),
            # "PLC 3,9MM        BC3067LOR6000*3210L0L00"
            "quality": raw.get("quality", ""),
            # "03"
            "previous_quality_code": raw.get("previousQualityCode", ""),
            # "03"
            "emballage": raw.get("c_embl", ""),
            # "026", "027"
            "package_type_code": raw.get("c_pile", ""),
            # "3067", "1013", "4015"
            "dimension_description": raw.get("ltmes", ""),
            # "PLF", "DLF"
            "length": raw.get("lon", ""),
            # "06000", "07000", "04500"
            "width": raw.get("lar", ""),
            # "02550", "03210"
            "treatment": raw.get("ltrai", ""),
            # "YES", "NONE"
            # ! "NONE" as string
            "thickness": raw.get("epaisn", ""),
            # "0390", "0800", "0590"
            "production_start_date": raw.get("productionStartDate", ""),
            # "2023-07-24 13:43:00"
            # ! date as string.
            "production_end_date": raw.get("productionEndDate", ""),
            # "2023-09-28 22:40:00"
            # ! date as string.
            "glass_age": int(float(raw["glassAge"])) if raw.get("glassAge") not in [None, ""] else None,
            # 6, 380, 381
            # <-- is int
            # <-- is also int in DB
            "age_date": raw.get("ageDate", ""),
            # "2023-09-29 04:37:00"
            # ! date as string.
            "wh_location_name": raw.get("whLocationName", ""),
            # "20R078", "E1R265"
            "production_line": raw.get("productionLine", ""),
            # "FSEZ", "T1.1"
            "interleaf_description": raw.get("lintv", ""),
            # "LUC",
            "primary_pack_material_id": raw.get("pri_ref", ""),
            # "SGG8625G", "VSG34", ""
            "primary_stillage_desc": raw.get("primaryStillageDesc", "")
            if raw.get("primaryStillageDesc") is not None
            else "",
            # "", "Virtual Stillage for Production         "
            "secondary_stillage_desc": raw.get("secondaryStillageDesc", "")
            if raw.get("secondaryStillageDesc") is not None
            else "",
            # null  <-- is "" in DB.
            "cover_sheet_id": raw.get("coverSheetId", ""),
            # ""
            "quality_status": raw.get("qualityStatus", ""),
            # "RAS", "ATT"
            "reason_code": raw.get("reasonCode", "") if raw.get("reasonCode") is not None else "",
            # null, "522", "606"
            # <-- null is "" in DB.
            "quality_comment_obs": raw.get("obs", ""),
            # "R000                                            ", ""
            "quality_comment_remarks": raw.get("remarks", "") if raw.get("remarks") is not None else "",
            # null
            # <-- null is "" in DB.
            "stacker": raw.get("stacker", ""),
            # "", "G1BM", "S9"
            "sap_order_no": raw.get("orderNo", ""),
            # "", "83624040"
            # ! can also be empty.
            "position_on_rack": int(float(raw["positionOnRack"]))
            # "22", "14", ""
            # ! can also be empty.
            if raw.get("positionOnRack") not in [None, ""] else None,
            # ! mixed type in DB (int, null).
            "nb_volumes": int(float(raw["nbVolumes"])) if raw.get("nbVolumes") not in [None, ""] else None,
            # "67", "5", "20"
            # <-- is int in DB.
            "sqm": float(raw["sqm"]) if raw.get("sqm") not in [None, ""] else None,
            # 847.44, 144.45    <-- is float
            # <-- is Decimal Field in DB.
            "tons": float(raw["tons"]) if raw.get("tons") not in [None, ""] else None,
            # 2.80857, 5.075973    <-- is float.
            # <-- is Decimal Field in DB.
        }
    except KeyError as key:
        log.warning(f"DataValidationError {key=}|{raw=}")
        raise DataValidationError(f"Failed to transform stock, missing key={key}.")
    except ValueError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError(f"Failed to transform stock, invalid value={e}.")
    return {attr: value for attr, value in stock.items() if value is not None}


def transform_purchase(raw: dict) -> dict:
    try:
        plant_id = raw["plant"]
    except KeyError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError("Failed to transform product, missing key 'plant' (plant division id).")
    plant, _ = Plant.objects.get_or_create(division=plant_id)

    try:
        purchases = {
            "plant": plant,
            "purchase_order_no": raw.get("purchaseOrderNo", ""),
            "sales_order_no": raw.get("salesOrderNo", "") if raw.get("salesOrderNo") is not None else "",
            "supplier_name": raw.get("supplierName", ""),
            "delivery_should_be_done": raw.get("dateDeliveryShouldBeDone", ""),
            "sap_material": raw.get("material", ""),
            "sap_technical_description": raw.get("l_article", ""),
            "ginger_code_17": raw.get("gingerCode17", ""),
            "package_type_code": raw.get("c_pile", ""),
            "coating": raw.get("lcoat", ""),
            "thickness": raw.get("epaisn", ""),
            "length": raw.get("lon", ""),
            "width": raw.get("lar", ""),
            "quality": raw.get("c_qual", ""),
            "order_quantity_volumes": float(raw["orderQtyVol"]) if raw.get("orderQtyVol") not in [None, ""] else None,
            "order_quantity_tons": float(raw["orderQtyTo"]) if raw.get("orderQtyTo") not in [None, ""] else None,
            "order_quantity_qm": float(raw["orderQtyM2"]) if raw.get("orderQtyM2") not in [None, ""] else None,
        }
    except KeyError as key:
        log.warning(f"DataValidationError {key=}|{raw=}")
        raise DataValidationError(f"Failed to transform purchase, missing key={key}.")
    except ValueError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError(f"Failed to transform purchase, invalid value={e}.")
    return {attr: value for attr, value in purchases.items() if value is not None}


def transform_order_management(raw: dict) -> dict:
    try:
        plant_id = raw["shippingPlant"]
        # "G035"
    except KeyError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError("Failed to transform product, missing key 'shippingPlant' (plant division id).")
    plant, _ = Plant.objects.get_or_create(division=plant_id)

    try:
        order_management = {
            "plant": plant,
            "expected_loading_date": raw.get("orderExpectedLoadingDate", ""),
            # "2023-10-20 00:00:00"  # ! date as string.
            "ship_to_customer": raw.get("shipToCustomer", ""),
            # "0000101536"  # ! leading zeros.
            "customer_name": raw.get("nom", ""),
            # "BOERMANS GLASINDUSTRIE 44822   N.V."
            # ! could null be possible here ?
            "country_code": raw.get("c_pays", ""),
            # "AT", "DE", "IS"
            "entry_date": raw.get("orderEntryDate", ""),
            # "2023-09-21 00:00:00"  # ! date as string.
            "sales_order": raw.get("salesOrder", ""),
            # "0061662482"  # ! leading zeros.
            "delivery_note": raw.get("deliveryNote", "") if raw.get("deliveryNote") is not None else "",
            # "0083618711", null  <-- null is "" in DB.
            "status": raw.get("orderStatus", ""),
            # "VALI", "RESA", "NEW"
            "reservation_project_name": raw.get("resaProjectName", ""),
            # " "  # ! string with empty space inside.
            "sap_material": raw.get("materialSapCode", ""),
            # "000000001000070536"  # ! leading zeros.
            "position": raw.get("_position", ""),
            # "000030", "000020", "000050"
            "ginger_code_17": raw.get("gingerCode17", ""),
            # "105608Q22T2250x3210T10240010"
            "sub_family": raw.get("lsfam", ""),
            # "STD SILENCE", "PLANILUX", "ECLAZ"
            "coating": raw.get("lcoat", ""),
            # "ECLAZ", "PLT XN", "NONE"
            # ! NONE as string.
            #   <-- is also "NONE" in DB.
            "tint": raw.get("ltein", ""),
            # "CLEAR", "EXTRACL"
            "thickness": raw.get("epaisn", ""),
            # "0490", "0800"  <-- is string.
            "dimension_description": raw.get("ltmes", ""),
            # "PLF", "DLF"
            "classification_lamination": raw.get("classificationLami", ""),
            # "NON LAMINATED", "OTHER LAMINATED GLASS"
            "quality": raw.get("c_qual", ""),
            # "03", "22"
            "treatment": raw.get("ltrai", ""),
            # "NONE"
            #   <-- is also "NONE" in DB.
            "package_type_family": raw.get("packFamily", ""),
            # "2,8t", "5,8t"
            "production_planning_class": raw.get("productionPlanningClass", ""),
            # "B0", "C1"
            "length": raw.get("lon", ""),
            # "03210", "06000"
            "width": raw.get("lar", ""),
            # "02250", "03210"
            "stock_place": raw.get("article027", ""),
            # "000000001010310030", "000000001010310030"
            # ! leading zeros.
            "package_type_code": raw.get("c_pile", ""),
            # "4014", "1014", "7028"
            "error_marker": raw.get("c_marq", ""),
            # "0"  <-- as string.
            "inter_product_layer": raw.get("c_intp", ""),
            # "0", "2"  <-- as string.
            "interleaf_description": raw.get("lintv", ""),
            # "LUC", "SPE"
            "order_quantity": float(raw["orderQuantity"]) if raw.get("orderQuantity") not in [None, ""] else None,
            # 150.0, 1.0, 9.0
            # ! mixed type in DB possible (float, null).
            "net_volumes_sqm": float(raw["netVolumesSqm"]) if raw.get("netVolumesSqm") not in [None, ""] else None,
            # 53.48749743589744
            # ! mixed type in DB possible (float, null).
            "net_weight_to": float(raw["netWeightTo"]) if raw.get("netWeightTo") not in [None, ""] else None,
            # 5.215031, 7.691096
            # ! mixed type in DB possible (float, null).
        }
    except KeyError as key:
        log.warning(f"DataValidationError {key=}|{raw=}")
        raise DataValidationError(f"Failed to transform order_management, missing key={key}.")
    except ValueError as e:
        log.warning(f"DataValidationError {e=}|{raw=}")
        raise DataValidationError(f"Failed to transform order_management, invalid value={e}.")
    return {attr: value for attr, value in order_management.items() if value is not None}
