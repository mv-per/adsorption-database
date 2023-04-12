from pathlib import Path
from typing import List

import numpy as np
import pytest

from adsorption_database.handlers.text_file_hander import (
    MixIsothermTextFileData,
    MonoIsothermTextFileData,
    TextFileHandler,
)
from adsorption_database.models.adsorbate import Adsorbate


def test_mono_file_handler(datadir: Path) -> None:

    handler = TextFileHandler(datadir)

    adsorbate = Adsorbate("adsorbate name", "adsorbate_formula")

    pure_data = MonoIsothermTextFileData(
        "pure_example.txt", adsorbate, 0, 1, pressure_conversion_factor_to_Pa=1e6
    )

    pressure, loadings = handler.get_mono_data(pure_data)

    assert type(pressure) == np.ndarray
    assert type(loadings) == np.ndarray

    assert pressure.shape == loadings.shape


def test_mix_file_handler(datadir: Path) -> None:

    handler = TextFileHandler(datadir)

    adsorbate1 = Adsorbate("adsorbate 1 name", "adsorbate_1_formula")
    adsorbate2 = Adsorbate("adsorbate 2 name", "adsorbate_2_formula")

    mixture_data = MixIsothermTextFileData(
        "mixture_example.txt",
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
