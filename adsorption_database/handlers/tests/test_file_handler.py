from pathlib import Path
from typing import List

import numpy as np
import pytest

from adsorption_database.handlers.text_file_hander import (
    MixIsothermTextFileData,
    MonoIsothermTextFileData,
    TextFileHandler,
)
from adsorption_database.helpers import Helpers
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.isotherms import IsothermType


def test_mono_file_handler(datadir: Path) -> None:

    handler = TextFileHandler(datadir)

    adsorbate = Adsorbate("adsorbate name", "adsorbate_formula")

    pure_data = MonoIsothermTextFileData("pure_example.txt", adsorbate, 0, 1)

    pressure, loadings = handler.get_mono_data(pure_data)

    assert type(pressure) == np.ndarray
    assert type(loadings) == np.ndarray

    assert pressure.shape == loadings.shape


def test_mono_file_handler_with_factors(datadir: Path) -> None:

    handler = TextFileHandler(datadir)

    adsorbate = Adsorbate("adsorbate name", "adsorbate_formula")

    pure_data = MonoIsothermTextFileData(
        "pure_example.txt",
        adsorbate,
        0,
        1,
    )

    pressure, loadings = handler.get_mono_data(pure_data)

    pure_data_with_factors = MonoIsothermTextFileData(
        "pure_example.txt",
        adsorbate,
        0,
        1,
        pressure_conversion_factor_to_Pa=1e6,
        loadings_conversion_factor_to_mol_per_kg=10,
    )

    pressure2, loadings2 = handler.get_mono_data(pure_data_with_factors)

    for p1, p2, n1, n2 in zip(pressure, pressure2, loadings, loadings2):
        assert pytest.approx(p2 / p1) == 1e6
        assert pytest.approx(n2 / n1) == 10


def test_mix_file_handler(datadir: Path) -> None:

    handler = TextFileHandler(datadir)

    adsorbate1 = Adsorbate("adsorbate 1 name", "adsorbate_1_formula")
    adsorbate2 = Adsorbate("adsorbate 2 name", "adsorbate_2_formula")

    mixture_data = MixIsothermTextFileData(
        "mixture_two_components_example.txt",
        [adsorbate1, adsorbate2],
        0,
        [2, 4],
        [1],
        load_missing_composition_from_equilibrium=True,
        pressure_conversion_factor_to_Pa=1e6,
    )

    pressure, loadings, compositions = handler.get_mix_data(mixture_data)

    assert type(pressure) == np.ndarray
    assert type(loadings) == np.ndarray
    assert type(compositions) == np.ndarray

    assert compositions.shape == loadings.shape


def test_mix_file_handler_with_factors(datadir: Path) -> None:

    handler = TextFileHandler(datadir)

    adsorbate1 = Adsorbate("adsorbate 1 name", "adsorbate_1_formula")
    adsorbate2 = Adsorbate("adsorbate 2 name", "adsorbate_2_formula")

    mixture_data = MixIsothermTextFileData(
        "mixture_two_components_example.txt",
        [adsorbate1, adsorbate2],
        0,
        [2, 4],
        [1],
        load_missing_composition_from_equilibrium=True,
    )

    pressure, loadings, _ = handler.get_mix_data(mixture_data)

    mixture_data2 = MixIsothermTextFileData(
        "mixture_two_components_example.txt",
        [adsorbate1, adsorbate2],
        0,
        [2, 4],
        [1],
        load_missing_composition_from_equilibrium=True,
        loadings_conversion_factor_to_mol_per_kg=10,
        pressure_conversion_factor_to_Pa=1e6,
    )

    pressure2, loadings2, _ = handler.get_mix_data(mixture_data2)

    for p1, p2, n1, n2 in zip(pressure, pressure2, loadings, loadings2):
        assert pytest.approx(p2 / p1) == 1e6

        for nn1, nn2 in zip(n1, n2):
            assert pytest.approx(nn2 / nn1) == 10


@pytest.mark.parametrize(
    "load_flag, composition_positions",
    [
        (True, [1, 2]),
        (False, [1, 2, 3]),
    ],
)
def test_mix_file_handler_tree_components(
    datadir: Path, load_flag: bool, composition_positions: List[int]
) -> None:

    handler = TextFileHandler(datadir)

    adsorbate1 = Adsorbate("adsorbate 1 name", "adsorbate_1_formula")
    adsorbate2 = Adsorbate("adsorbate 2 name", "adsorbate_2_formula")
    adsorbate3 = Adsorbate("adsorbate 3 name", "adsorbate_3_formula")

    mixture_data = MixIsothermTextFileData(
        "mixture_tree_components_example.txt",
        [adsorbate1, adsorbate2, adsorbate3],
        0,
        [4, 5, 6],
        composition_positions,
        load_missing_composition_from_equilibrium=load_flag,
        pressure_conversion_factor_to_Pa=1e6,
    )

    pressure, loadings, compositions = handler.get_mix_data(mixture_data)

    assert type(pressure) == np.ndarray
    assert type(loadings) == np.ndarray
    assert type(compositions) == np.ndarray

    assert compositions.shape == loadings.shape


def test_mix_file_handler_raise_index_error(datadir: Path) -> None:

    handler = TextFileHandler(datadir)

    adsorbate1 = Adsorbate("adsorbate 1 name", "adsorbate_1_formula")
    adsorbate2 = Adsorbate("adsorbate 2 name", "adsorbate_2_formula")
    adsorbate3 = Adsorbate("adsorbate 3 name", "adsorbate_3_formula")

    mixture_data = MixIsothermTextFileData(
        "mixture_tree_components_example.txt",
        [adsorbate1, adsorbate2, adsorbate3],
        0,
        [4, 5, 6],
        [1, 2],
        load_missing_composition_from_equilibrium=False,
        pressure_conversion_factor_to_Pa=1e6,
    )

    with pytest.raises(IndexError):
        handler.get_mix_data(mixture_data)


def test_create_mono_isotherm(
    datadir: Path, data_regression, helpers: Helpers
) -> None:

    handler = TextFileHandler(datadir)

    adsorbate = Adsorbate("adsorbate name", "adsorbate_formula")

    pure_data = MonoIsothermTextFileData(
        "pure_example.txt",
        adsorbate,
        0,
        1,
    )

    mono_isotherm = handler.create_mono_isotherm(
        "isotherm 1", 300, IsothermType.ABSOLUTE, pure_data
    )

    assert mono_isotherm


def test_create_mix_isotherm(
    co2_adsorbate: Adsorbate,
    ch4_adsorbate: Adsorbate,
    datadir: Path,
    data_regression,
    helpers: Helpers,
) -> None:

    handler = TextFileHandler(datadir)

    mixture_data = MixIsothermTextFileData(
        "mixture_two_components_example.txt",
        [co2_adsorbate, ch4_adsorbate],
        0,
        [2, 4],
        [1],
        load_missing_composition_from_equilibrium=True,
        pressure_conversion_factor_to_Pa=1e6,
    )

    isotherm = handler.create_mix_isotherm(
        "isotherm 1", 300, IsothermType.ABSOLUTE, mixture_data
    )

    assert isotherm
