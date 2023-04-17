from pathlib import Path
import numpy as np
import pytest
from pytest_mock import MockerFixture
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.isotherms import IsothermType, MixIsotherm, MonoIsotherm
from adsorption_database.helpers import Helpers
from adsorption_database.storage_provider import StorageProvider


pressures = np.arange(10, dtype="float64")
loadings_1 = np.linspace(20, 50, 10, dtype="float64")
loadings_2 = np.linspace(50, 20, 10, dtype="float64")
x_1 = np.linspace(0, 1, 10, dtype="float64")
x_2 = np.array([1 - val for val in list(x_1)], dtype="float64")


@pytest.fixture
def co2_adsorbate() -> Adsorbate:
    return Adsorbate(name="Carbon Dioxide", chemical_formula="CO2")


@pytest.fixture
def ch4_adsorbate() -> Adsorbate:
    return Adsorbate(name="Methane", chemical_formula="CH4")


@pytest.fixture
def mono_isotherm(co2_adsorbate: Adsorbate) -> MonoIsotherm:
    return MonoIsotherm(
        name="Mono Isotherm",
        isotherm_type=IsothermType.EXCESS,
        adsorbate=co2_adsorbate,
        pressures=pressures,
        loadings=loadings_1,
        temperature=300,
    )

@pytest.fixture
def mono_isotherm_with_heats_of_adsorption(co2_adsorbate: Adsorbate) -> MonoIsotherm:
    return MonoIsotherm(
        name="Mono Isotherm",
        isotherm_type=IsothermType.EXCESS,
        adsorbate=co2_adsorbate,
        pressures=pressures,
        loadings=loadings_1,
        heats_of_adsorption=loadings_1,
        temperature=300,
    )


@pytest.fixture
def mix_isotherm(co2_adsorbate: Adsorbate, ch4_adsorbate: Adsorbate) -> MixIsotherm:
    return MixIsotherm(
        name="Mix Isotherm",
        isotherm_type=IsothermType.EXCESS,
        adsorbates=[co2_adsorbate, ch4_adsorbate],
        pressures=pressures,
        comments="this is a mock isotherm",
        loadings=np.array([loadings_1, loadings_2], dtype="float64"),
        bulk_composition=np.array([x_1, x_2], dtype="float64"),
        temperature=300,
    )


@pytest.fixture
def helpers() -> Helpers:
    return Helpers()
