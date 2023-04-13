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


@pytest.fixture(autouse=True)
def setup_storage(datadir: Path, mocker: MockerFixture) -> Path:
    storage_path = Path(datadir / "test_storage.hdf5")

    mocker.patch.object(StorageProvider, "get_file_path", return_value=storage_path)

    return storage_path


def test_get_isotherm_store_name(mono_isotherm: MonoIsotherm) -> None:
    handler = TestAbstractHandler()
    assert handler.get_isotherm_store_name(mono_isotherm) == "Mono Isotherm-Excess"


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


def test_register_experiment(
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
        temperature=318.2,
        monocomponent_isotherms=[mono_isotherm],
        mixture_isotherms=[mix_isotherm],
    )

    handler.register_experiment(experiment)

    storage_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": storage_tree})


def test_get_groups() -> None:

    handler = TestAbstractHandler()

    with StorageProvider().get_editable_file() as f:
        assert MONO_ISOTHERMS not in list(f)
        assert MIXTURE_ISOTHERMS not in list(f)
        assert EXPERIMENTS not in list(f)

        handler.get_mono_isotherm_group(f)
        handler.get_mix_isotherm_group(f)
        handler.get_experiment_group(f)
        assert MONO_ISOTHERMS in list(f)
        assert MIXTURE_ISOTHERMS in list(f)
        assert EXPERIMENTS in list(f)

        # test a second load
        handler.get_mono_isotherm_group(f)
        handler.get_mix_isotherm_group(f)
        handler.get_experiment_group(f)


def test_upsert_dataset() -> None:

    handler = TestAbstractHandler()

    dataset_name = "my_dataset"
    with StorageProvider().get_editable_file() as f:
        assert dataset_name not in list(f)

        # Test creating dataset
        dataset_values = np.array([1, 2, 3, 4, 5, 6, 7], dtype="float64")
        handler.upsert_dataset(f, dataset_name, dataset_values)
        assert (np.array(f[dataset_name]) == dataset_values).all()

        # Test updating dataset to a different shape
        dataset_values = np.array([8, 9, 10, 11, 12], dtype="float64")
        handler.upsert_dataset(f, dataset_name, dataset_values)
        assert (np.array(f[dataset_name]) == dataset_values).all()

        # Test updating dataset to a different shape increazing column
        a = np.array([1, 2, 3, 4, 5, 6, 7], dtype="float64")
        b = np.array([8, 9, 10, 11, 12, 13, 14], dtype="float64")
        assert (
            a.shape == b.shape
        )  # Without ensuring the same length, the new dataset will have type 'O', causing an error in the upsert method
        dataset_values = np.array([a, b])

        handler.upsert_dataset(f, dataset_name, dataset_values)
        assert (np.array(f[dataset_name]) == dataset_values).all()


def test_upsert_dataset_type_o_error() -> None:

    handler = TestAbstractHandler()

    dataset_name = "my_dataset"

    with StorageProvider().get_editable_file() as f:
        a = np.array([1, 2, 3, 4, 5, 6, 7], dtype="float64")
        b = np.array([4, 5, 6], dtype="float64")
        dataset_values = np.array([a, b])

        with pytest.raises(TypeError) as exc_info:
            handler.upsert_dataset(f, dataset_name, dataset_values)

        assert str(exc_info.value) == "Object dtype dtype('O') has no native HDF5 equivalent"


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
        experiments_groups = handler.get_experiment_group(f)
        experiment_group = handler.get_group(experiment_name, experiments_groups)

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
        experiments_groups = handler.get_experiment_group(f)
        experiment_group = handler.get_group(experiment_name, experiments_groups)

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
        temperature=318.2,
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
