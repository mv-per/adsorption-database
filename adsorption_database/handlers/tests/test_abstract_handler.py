from pathlib import Path
from typing import Tuple
import numpy as np
from adsorption_database.defaults import (
    ADSORBATES,
    ADSORBENTS,
    EXPERIMENTS,
    MIXTURE_ISOTHERMS,
    MONO_ISOTHERMS,
)
from adsorption_database.handlers.abstract_handler import AbstractHandler
import pytest
import os
from pytest_mock import MockerFixture
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.adsorbent import Adsorbent, AdsorbentType
from adsorption_database.models.experiment import Experiment, ExperimentType
from adsorption_database.shared import (
    get_experiments_group,
    get_isotherm_store_name,
    get_mix_isotherm_group,
    get_mono_isotherm_group,
)
from adsorption_database.storage_provider import StorageProvider
from adsorption_database.models.isotherms import (
    MixIsotherm,
    MixIsothermFileData,
    MonoIsotherm,
    MonoIsothermFileData,
)
import numpy.typing as npt
from pytest_regressions.data_regression import DataRegressionFixture
from adsorption_database.helpers import Helpers


class TestAbstractHandler(AbstractHandler[MonoIsothermFileData, MixIsothermFileData]):
    def get_mono_data(
        self, file_data: MonoIsothermFileData
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        return super().get_mono_data(file_data)

    def get_mix_data(
        self, file_data: MixIsothermFileData
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        return super().get_mix_data(file_data)


def test_get_isotherm_store_name(mono_isotherm: MonoIsotherm) -> None:
    assert get_isotherm_store_name(mono_isotherm) == "Mono Isotherm-Excess"


def test_register_adsorbate(
    co2_adsorbate: Adsorbate,
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:
    handler = TestAbstractHandler()

    handler.register_adsorbate(co2_adsorbate)

    storage_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": storage_tree})


def test_register_experiment_and_dump(
    co2_adsorbate: Adsorbate,
    ch4_adsorbate: Adsorbate,
    mix_isotherm: MixIsotherm,
    mono_isotherm: MonoIsotherm,
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:

    handler = TestAbstractHandler()

    handler.register_adsorbate(co2_adsorbate)
    handler.register_adsorbate(ch4_adsorbate)

    z01x = Adsorbent(name="z01x", type=AdsorbentType.ZEOLITE)

    handler.register_adsorbent(z01x)

    experiment = Experiment(
        name="Sudi",
        authors=["a", "b", "c"],
        adsorbent=z01x,
        experiment_type=ExperimentType.VOLUMETRIC,
        monocomponent_isotherms=[mono_isotherm],
        mixture_isotherms=[mix_isotherm],
    )

    handler.register_experiment(experiment)

    storage_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": storage_tree})


def test_register_mono_isotherm(
    co2_adsorbate: Adsorbate,
    mono_isotherm: MonoIsotherm,
    helpers: Helpers,
    data_regression: DataRegressionFixture,
    setup_storage: Path,
) -> None:

    handler = TestAbstractHandler()

    handler.register_adsorbate(co2_adsorbate)

    with StorageProvider().get_editable_file() as f:

        experiment_name = "EXP-01"
        experiments_groups = get_experiments_group(f)
        experiment_group = experiments_groups.require_group(experiment_name)

        handler.register_mono_isotherm(mono_isotherm, experiment_group)

    storage_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": storage_tree})


def test_register_mix_isotherm(
    co2_adsorbate: Adsorbate,
    ch4_adsorbate: Adsorbate,
    mix_isotherm: MixIsotherm,
    helpers: Helpers,
    data_regression: DataRegressionFixture,
    setup_storage: Path,
) -> None:

    handler = TestAbstractHandler()

    handler.register_adsorbate(co2_adsorbate)
    handler.register_adsorbate(ch4_adsorbate)

    with StorageProvider().get_editable_file() as f:

        experiment_name = "EXP-01"
        experiments_groups = get_experiments_group(f)
        experiment_group = experiments_groups.require_group(experiment_name)

        handler.register_mix_isotherm(mix_isotherm, experiment_group)

    storage_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": storage_tree})


def test_register_experiment(
    mono_isotherm: MonoIsotherm,
    co2_adsorbate: Adsorbate,
    ch4_adsorbate: Adsorbate,
    mix_isotherm: MixIsotherm,
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:

    handler = TestAbstractHandler()

    handler.register_adsorbate(co2_adsorbate)
    handler.register_adsorbate(ch4_adsorbate)

    z01x = Adsorbent(name="z01x", type=AdsorbentType.ZEOLITE)

    handler.register_adsorbent(z01x)

    experiment = Experiment(
        name="Sudi",
        authors=["a", "b", "c"],
        adsorbent=z01x,
        experiment_type=ExperimentType.VOLUMETRIC,
        monocomponent_isotherms=[mono_isotherm],
        mixture_isotherms=[mix_isotherm],
    )

    handler.register_experiment(experiment)

    storage_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": storage_tree})


def test_not_implemented_mono(co2_adsorbate: Adsorbate) -> None:

    handler = TestAbstractHandler()

    file = MonoIsothermFileData(file_name="test", adsorbate=co2_adsorbate)

    with pytest.raises(NotImplementedError):
        handler.get_mono_data(file)


def test_not_implemented_mix(co2_adsorbate: Adsorbate) -> None:

    handler = TestAbstractHandler()

    file = MixIsothermFileData(file_name="test", adsorbates=[co2_adsorbate])

    with pytest.raises(NotImplementedError):
        handler.get_mix_data(file)
