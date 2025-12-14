-- -    I struggle to retrieve good results especially for “order management”
--      as the join/merge does not seem to work. It keeps building cartesian
--      products instead of displaying unique lines. I may delete duplicate
--      lines via distinct, however, I hope that you have a better proposal

-- Ordermanagement query
SELECT a.shipping_plant, a.order_expected_loading_date, a.ship_to_customer, b.CUSTOMER_NAME, b.COUNTRY_SOLD_TO, a.order_entry_date, a.sales_order, a.deliverynote, a.order_status, a.resa_project_name,
a.material_sap_code, a._position, a.order_quantity, a.net_volumes_sqm, a.net_weight_to, LEFT(d.ginger_code_17_, 28) as ginger_code_17, c.lsfam, c.lcoat, c.ltein, c.epaisn, c.ltmes,
c.classification_lami, c.c_qual, c.ltrai, c.pack_family, d.dschart, c.lon, c.lar, e.article_027, c.c_pile, c.c_marq, c.c_intp, c.lintv
FROM smart_sap_book_orders as a
LEFT JOIN board_customer_md as b
ON a.ship_to_customer = b.CUSTOMER
LEFT JOIN smart_extract_sap_article as c
ON a.material_sap_code = c.c_article
LEFT JOIN smart_extract_sap_article_ginger as d
ON a.material_sap_code = d.c_article
LEFT JOIN smart_orion_sap_stock_doctrine as e
on LEFT(d.ginger_code_17_, 28) = e.ginger_code_17
WHERE a.shipping_plant = 'G035'
AND a.shipped_flag = 'N'
AND a.order_expected_loading_date > DATEADD(DAY, -14, GETDATE())
AND a.order_expected_loading_date < DATEADD(DAY, 180, GETDATE())
AND c.c_pile NOT IN (1001, 2001, 6001, 7001, 8001)
AND a.order_status NOT IN ('CANC')








-- Stock query
SELECT a.IDSheet, a.Positiononrack, a.NBVolumes, a.Material, c.l_article, c.c_qual AS Quality, a.PreviousQualitycode, c.c_embl,
c.c_pile, c.ltmes, c.lon, c.lar, c.ltrai, c.epaisn,
a.Productionstartdate, a.Productionenddate, a.GlassAge, a.AgeDate, a.WHlocationname, a.Productionline, a.Origin, c.lintv, a.pri_ref,
a.Primary_stillage_desc, a.Secondary_stillage_desc, a.SQM, a.Tons, a.Coversheetid,
a.Qualitystatus, a.REASON_CODE, a.obs,  b.remarks, a.Stacker, a.Orderno
FROM smart_orion_stock AS a
LEFT JOIN smart_orion_stock_derog_info as b
ON a.IDSheet = b.c_fich
LEFT JOIN smart_extract_sap_article AS c
ON a.Material = RIGHT(c.c_article, 10)
WHERE Plant = "G035";-- Stock query
SELECT a.IDSheet, a.Positiononrack, a.NBVolumes, a.Material, a.PreviousQualitycode,
a.Productionstartdate, a.Productionenddate, a.GlassAge, a.AgeDate, a.WHlocationname, a.Productionline, a.pri_ref,
a.Primary_stillage_desc, a.Secondary_stillage_desc, a.IDSheetStatus, a.SQM, a.Tons, a.Coversheetid, a.obs, a.Qualitystatus, a.REASON_CODE, a.Stacker, a.Orderno, b.remarks
FROM smart_orion_stock AS AgeDate
LEFT JOIN smart_orion_stock_derog_info as b
ON a.IDSheet = b.IDSheet AND a.c_fich = b.c_fich
WHERE Plant = "G035";

-- Purchases query
SELECT a.plant, a.purchaseorderno, a.saleorderno, a.suppliername, a.datedeliveryshouldbedone, a.material,
b.l_article, a.ginger_code_17, b.c_pile, b.lcoat, b.epaisn, b.lon, b.lar, b.c_qual,
a.orderqtyvol, a.orderqtyto, a.orderqtym2

FROM sgg.smart_sap_purchase as a
LEFT JOIN sgg.smart_extract_sap_article as b
ON a.material = b.c_article

WHERE a.receptionflag NOT IN ('Y')
AND a.plant = 'G035'
AND a.ginger_code_17 REGEXP '^1'
AND a.datedeliveryshouldbedone > DATEADD(DAY, -14, GETDATE())
;

-- products query
SELECT a.c_divi, LEFT(a.ginger_code_17_, 28) as ginger_code_17, a.c_article, a.l_article, a.typ_appro, a.dschart, a.dzeit, a.stksecumin, a.meins, b.havp, c.c_embl, c.lembl, c.lib_com, c.lg_short_description,
c.lg_long_description, c.c_article_lg, c.lfam, c.lsfam, c.lcoat, c.limpr, c.ltein, c.c_qual, c.ltrai, c.epaisn, c.lqual, c.ltmes, c.dimension, c.lon, c.lar, c.c_pile, c.pack_family, c.lstri, c.c_marq,
c.c_intp, c.lintv, d.safety_time, d.safety_stock_ton, d.production_lead_time, e.cut_pmm_plf, e.size_t_mm

FROM smart_extract_sap_article_ginger as a
LEFT JOIN smart_sap_havp as b
ON a.c_article = b.c_article
LEFT JOIN smart_extract_sap_article as c
ON a.c_article = c.c_article
LEFT JOIN smart_orion_sap_stock_doctrine as d
ON LEFT(a.ginger_code_17_, 28) = d.ginger_code_17
LEFT JOIN smart_sap_article as e
ON a.c_article = e.c_article

WHERE a.c_divi = 'G035'
AND a.deletion_flag_plant_level NOT IN ('X')
