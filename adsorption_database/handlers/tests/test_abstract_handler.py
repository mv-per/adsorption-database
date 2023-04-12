from pathlib import Path
from typing import Tuple
import numpy as np
from adsorption_database.defaults import ADSORBATES, EXPERIMENTS, MIXTURE_ISOTHERMS, MONO_ISOTHERMS
from adsorption_database.handlers.abstract_handler import AbstractHandler
import pytest
import os
from pytest_mock import MockerFixture
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.storage_provider import StorageProvider
from adsorption_database.models.isotherms import (
    MixIsotherm,
    MixIsothermFileData,
    MonoIsotherm,
    MonoIsothermFileData,
)
import numpy.typing as npt

from conftest import Helpers


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
def setup_storage(datadir: Path, mocker: MockerFixture) -> None:
    storage_path = Path(datadir / "test_storage.hdf5")

    if storage_path.exists():
        os.remove(storage_path.resolve())

    mocker.patch.object(StorageProvider, "get_file_path", return_value=storage_path)


def test_get_isotherm_store_name(mono_isotherm: MonoIsotherm) -> None:
    handler = TestAbstractHandler()
    assert handler.get_isotherm_store_name(mono_isotherm) == "Mono Isotherm-Excess"


def test_register_adsorbate(co2_adsorbate: Adsorbate, helpers: Helpers) -> None:
    handler = TestAbstractHandler()

    handler.register_adsorbate(co2_adsorbate)

    with StorageProvider().get_readable_file() as file:
        assert "Carbon Dioxide" in list(file[ADSORBATES])
        helpers.check_registered_adsorbate(co2_adsorbate, file[ADSORBATES]["Carbon Dioxide"])


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
    co2_adsorbate: Adsorbate, mono_isotherm: MonoIsotherm, helpers: Helpers
) -> None:

    handler = TestAbstractHandler()

    handler.register_adsorbate(co2_adsorbate)

    with StorageProvider().get_editable_file() as f:

        experiment_name = "EXP-01"
        experiments_groups = handler.get_experiment_group(f)
        experiment_group = handler.get_group(experiment_name, experiments_groups)

        handler.register_mono_isotherm(mono_isotherm, experiment_group)

        assert ADSORBATES in list(f)
        assert experiment_name in list(f[EXPERIMENTS])
        assert MONO_ISOTHERMS in list(f[EXPERIMENTS][experiment_name])

        registered_isotherm = f[
            f"{EXPERIMENTS}/{experiment_name}/{MONO_ISOTHERMS}/{mono_isotherm.name}-{mono_isotherm.isotherm_type.value}"
        ]

        assert "loadings" in list(registered_isotherm)
        assert "pressures" in list(registered_isotherm)

        assert (registered_isotherm["loadings"] == mono_isotherm.loadings).all()
        assert (registered_isotherm["pressures"] == mono_isotherm.pressures).all()

        helpers.check_registered_adsorbate(co2_adsorbate, registered_isotherm["adsorbate"])

        for attr_ in ["name"]:
            assert attr_ in list(registered_isotherm.attrs)
            assert registered_isotherm.attrs[attr_] == getattr(mono_isotherm, attr_)


def test_register_mix_isotherm(
    co2_adsorbate: Adsorbate, ch4_adsorbate: Adsorbate, mix_isotherm: MixIsotherm, helpers: Helpers
) -> None:

    handler = TestAbstractHandler()

    handler.register_adsorbate(co2_adsorbate)
    handler.register_adsorbate(ch4_adsorbate)

    with StorageProvider().get_editable_file() as f:

        experiment_name = "EXP-01"
        experiments_groups = handler.get_experiment_group(f)
        experiment_group = handler.get_group(experiment_name, experiments_groups)

        handler.register_mix_isotherm(mix_isotherm, experiment_group)

        assert ADSORBATES in list(f)
        assert experiment_name in list(f[EXPERIMENTS])
        assert MIXTURE_ISOTHERMS in list(f[EXPERIMENTS][experiment_name])

        registered_isotherm = f[
            f"{EXPERIMENTS}/{experiment_name}/{MIXTURE_ISOTHERMS}/{mix_isotherm.name}-{mix_isotherm.isotherm_type.value}"
        ]

        assert (registered_isotherm["loadings"] == mix_isotherm.loadings).all()
        assert (registered_isotherm["pressures"] == mix_isotherm.pressures).all()
        assert (registered_isotherm["bulk_composition"] == mix_isotherm.bulk_composition).all()

        for adsorbate, registered_adsorbate in zip(
            [co2_adsorbate, ch4_adsorbate], registered_isotherm["adsorbates"]
        ):
            group = handler.get_group(registered_adsorbate.decode(), f)
            helpers.check_registered_adsorbate(adsorbate, group)

        for attr_ in ["name"]:
            assert attr_ in list(registered_isotherm.attrs)
            assert registered_isotherm.attrs[attr_] == getattr(mix_isotherm, attr_)
