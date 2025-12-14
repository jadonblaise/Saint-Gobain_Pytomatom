import random

import pytest

from apps.datalake.models import GlassPane
from test.factories.datalake import pane_factory, plant_factory


@pytest.fixture
def plant():
    _plant = plant_factory(division="G035")
    yield _plant
    _plant.delete()


@pytest.fixture
def pane(plant):
    _pane = pane_factory(plant=plant)
    yield _pane
    _pane.delete()


@pytest.fixture
def sap_materials():
    """
    Five real SAP materials to randomly assign to random panes.
    """
    yield ["1056080059", "1056080060", "1056080061", "1056080062", "1056080063"]


@pytest.fixture
def panes(plant, sap_materials):
    created = [pane_factory(plant=plant, sap_material=random.choice(sap_materials)) for _ in range(50)]
    _panes = GlassPane.objects.filter(id__in=[p.id for p in created])
    yield _panes
    for pane in created:
        pane.delete()
