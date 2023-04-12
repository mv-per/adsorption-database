from typing import Type
import numpy as np
import pytest
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.isotherms import IsothermType, MixIsotherm, MonoIsotherm
import h5py


class Helpers:
    @staticmethod
    def check_registered_adsorbate(adsorbate: Adsorbate, registered_adsorbate: h5py.Group) -> None:
        assert adsorbate.name == registered_adsorbate.attrs["name"]
        assert adsorbate.chemical_formula == registered_adsorbate.attrs["chemical_formula"]


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
    )


@pytest.fixture
def mix_isotherm(co2_adsorbate: Adsorbate, ch4_adsorbate: Adsorbate) -> MixIsotherm:
    return MixIsotherm(
        name="Mix Isotherm",
        isotherm_type=IsothermType.EXCESS,
        adsorbates=[co2_adsorbate, ch4_adsorbate],
        pressures=pressures,
        loadings=np.array([loadings_1, loadings_2], dtype="float64"),
        bulk_composition=np.array([x_1, x_2], dtype="float64"),
    )


@pytest.fixture
def helpers() -> Helpers:
    return Helpers()
