from decimal import Decimal
from typing import Any

from faker import Factory as FakerFactory

from django.conf import settings

from apps.datalake.models import Plant, GlassPane
from core.cypher.tokens import urlsafe_token


# for all providers see: https://faker.readthedocs.io/en/master/providers.html
# typehinting for faker is not available yet, so we have to use Any
faker: Any = FakerFactory.create()
# ! Faker will have a seed in test mode
faker.seed(settings.TEST_FAKER_SEED)  # type: ignore[misc]


def plant_factory(
    *,
    division: str = "",
) -> Plant:  # type: ignore
    division = division if division else faker.word()
    plant = Plant.objects.create(division=division)
    return plant


def pane_factory(  # NOSONAR
    *,  # NOSONAR
    plant: Plant,
    sheet_id: str = "",
    sap_material: str = "",
    sap_technical_description: str = "",
    quality: str = "",
    previous_quality_code: str = "",
    emballage: str = "",
    package_type_code: str = "",
    dimension_description: str = "",
    length: str = "",
    width: str = "",
    treatment: str = "",
    thickness: str = "",
    production_start_date: str = "",
    production_end_date: str = "",
    glass_age: int | None = None,
    age_date: str = "",
    wh_location_name: str = "",
    production_line: str = "",
    interleaf_description: str = "",
    primary_pack_material_id: str = "",
    primary_stillage_desc: str = "",
    secondary_stillage_desc: str = "",
    cover_sheet_id: str = "",
    quality_status: str = "",
    reason_code: str = "",
    quality_comment_obs: str = "",
    quality_comment_remarks: str = "",
    stacker: str = "",
    sap_order_no: str = "",
    position_on_rack: int | None = None,
    nb_volumes: int | None = None,
    sqm: Decimal | None = None,
    tons: Decimal | None = None,
) -> GlassPane:  # type: ignore
    sheet_id = sheet_id if sheet_id else urlsafe_token()
    sap_material = sap_material if sap_material else faker.word()
    sap_technical_description = sap_technical_description if sap_technical_description else faker.word()
    quality = quality if quality else faker.word()
    previous_quality_code = previous_quality_code if previous_quality_code else faker.word()
    emballage = emballage if emballage else faker.word()
    package_type_code = package_type_code if package_type_code else faker.word()
    dimension_description = dimension_description if dimension_description else faker.word()
    length = length if length else faker.word()
    width = width if width else faker.word()
    treatment = treatment if treatment else faker.word()
    thickness = thickness if thickness else faker.word()
    production_start_date = production_start_date if production_start_date else faker.word()
    production_end_date = production_end_date if production_end_date else faker.word()

    glass_age = glass_age if glass_age is not None else faker.random_int(min=0, max=100)

    age_date = age_date if age_date else faker.word()
    wh_location_name = wh_location_name if wh_location_name else faker.word()
    production_line = production_line if production_line else faker.word()
    interleaf_description = interleaf_description if interleaf_description else faker.word()
    primary_pack_material_id = primary_pack_material_id if primary_pack_material_id else faker.word()
    primary_stillage_desc = primary_stillage_desc if primary_stillage_desc else faker.word()
    secondary_stillage_desc = secondary_stillage_desc if secondary_stillage_desc else faker.word()
    cover_sheet_id = cover_sheet_id if cover_sheet_id else faker.word()
    quality_status = quality_status if quality_status else faker.word()
    reason_code = reason_code if reason_code else faker.word()
    quality_comment_obs = quality_comment_obs if quality_comment_obs else faker.word()
    quality_comment_remarks = quality_comment_remarks if quality_comment_remarks else faker.word()
    stacker = stacker if stacker else faker.word()
    sap_order_no = sap_order_no if sap_order_no else faker.word()

    position_on_rack = position_on_rack if position_on_rack is not None else faker.random_int(min=0, max=100)
    nb_volumes = nb_volumes if nb_volumes is not None else faker.random_int(min=0, max=100)
    sqm = sqm if sqm is not None else Decimal(faker.pyfloat(left_digits=2, right_digits=2, positive=True))
    tons = tons if tons is not None else Decimal(faker.pyfloat(left_digits=2, right_digits=2, positive=True))

    pane = GlassPane.objects.create(
        plant=plant,
        sheet_id=sheet_id,
        sap_material=sap_material,
        sap_technical_description=sap_technical_description,
        quality=quality,
        previous_quality_code=previous_quality_code,
        emballage=emballage,
        package_type_code=package_type_code,
        dimension_description=dimension_description,
        length=length,
        width=width,
        treatment=treatment,
        thickness=thickness,
        production_start_date=production_start_date,
        production_end_date=production_end_date,
        glass_age=glass_age,
        age_date=age_date,
        wh_location_name=wh_location_name,
        production_line=production_line,
        interleaf_description=interleaf_description,
        primary_pack_material_id=primary_pack_material_id,
        primary_stillage_desc=primary_stillage_desc,
        secondary_stillage_desc=secondary_stillage_desc,
        cover_sheet_id=cover_sheet_id,
        quality_status=quality_status,
        reason_code=reason_code,
        quality_comment_obs=quality_comment_obs,
        quality_comment_remarks=quality_comment_remarks,
        stacker=stacker,
        sap_order_no=sap_order_no,
        position_on_rack=position_on_rack,
        nb_volumes=nb_volumes,
        sqm=sqm,
        tons=tons,
    )
    return pane
