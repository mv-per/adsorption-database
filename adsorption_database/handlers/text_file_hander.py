from pathlib import Path
from typing import Any, List, Optional, Tuple

from attr import define
from adsorption_database.models import (
    MonoIsothermFileData,
    MixIsothermFileData,
)
from adsorption_database.handlers.abstract_handler import AbstractHandler
import numpy as np

import numpy.typing as npt

from collections import namedtuple

GetLoadingsFromAdsorbed = namedtuple(
    "GetLoadingsFromAdsorbed", "get_missing_x_from_eq pos_x pos_nt"
)


@define
class MonoIsothermTextFileData(MonoIsothermFileData):
    pressures_col: int
    loadings_col: int
    pressure_conversion_factor_to_Pa: Optional[float] = None
    loadings_conversion_factor_to_mol_per_kg: Optional[float] = None
    filter_duplicate: bool = False


@define
class MixIsothermTextFileData(MixIsothermFileData):
    pressures_col: int
    loadings_cols: List[int]
    composition_cols: List[int]
    load_missing_composition_from_equilibrium: Optional[bool] = False
    pressure_conversion_factor_to_Pa: Optional[float] = None
    loadings_conversion_factor_to_mol_per_kg: Optional[float] = None
    get_loadings_from_adsorbed: Optional[GetLoadingsFromAdsorbed] = None
    filter_duplicate: bool = False


class TextFileHandler(
    AbstractHandler[MonoIsothermTextFileData, MixIsothermTextFileData]
):
    """
    A class for handling text files containing isotherm data.

    This class provides methods for reading and processing isotherm data from text files, including single-component
    and multi-component isotherms.
    """

    def __init__(self, folder: Path) -> None:
        """
        Constructor to initialize the TextFileHandler object.

        Args:
            folder (Optional[Path]): The folder path where the text files are located. Defaults to None, in which case
            the default folder path will be used.

        Returns:
            None
        """
        super().__init__()
        self._folder_path = folder

    def get_mono_data(
        self, file_data: MonoIsothermTextFileData
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """
        Method to get single-component isotherm data from a text file.

        Args:
            file_data (MonoIsothermTextFileData): An object containing information about the file, its data columns,
            and conversion factors for pressure and loading.

        Returns:
            Tuple[List[float], List[float]]: A tuple containing two lists: pressures and loadings.
        """
        file_path = self._folder_path / file_data.file_name

        file = np.loadtxt(file_path)
        pressures = file[:, file_data.pressures_col]
        loadings = file[:, file_data.loadings_col]

        # remove_duplicates
        if file_data.filter_duplicate:
            pairs = [(p, n) for p, n in zip(pressures, loadings)]

            filtered_pairs = []
            for pair in pairs:
                if pair in filtered_pairs:
                    continue
                filtered_pairs.append(pair)

            pressures = [float(val[0]) for val in filtered_pairs]
            loadings = [float(val[1]) for val in filtered_pairs]

        p_factor = file_data.pressure_conversion_factor_to_Pa
        if p_factor is not None:
            pressures = [p * p_factor for p in pressures]

        n_factor = file_data.loadings_conversion_factor_to_mol_per_kg
        if n_factor is not None:
            loadings = [n * n_factor for n in loadings]

        pressures = np.array(pressures, dtype=np.float64)
        loadings = np.array(loadings, dtype=np.float64)

        assert pressures.shape == loadings.shape

        return pressures, loadings

    def get_bulk_composition(
        self,
        file: Any,
        file_data: MixIsothermFileData,
        pressures: npt.NDArray[np.float64],
    ) -> npt.NDArray[np.float64]:
        compositions_list: List[npt.NDArray[np.float64]] = []
        for index in range(len(file_data.adsorbates)):
            try:
                component_compositions = file[:, file_data.composition_cols[index]]  # type: ignore[attr-defined]
            except IndexError:
                if file_data.load_missing_composition_from_equilibrium:  # type: ignore[attr-defined]
                    component_compositions = []

                    for index in range(len(pressures)):
                        x_sum = 0
                        for comp in compositions_list:
                            x_sum += list(comp)[index]
                        component_compositions.append(1 - x_sum)
                else:
                    raise
            compositions_list.append(np.array(component_compositions))

        return np.array(compositions_list)

    def get_loadings_from_adsorbed_compositions(
        self,
        file: Any,
        file_data: MixIsothermFileData,
        pressures: npt.NDArray[np.float64],
    ) -> npt.NDArray[np.float64]:
        adsorbed_x_list: List[npt.NDArray[np.float64]] = []
        loadings_list: List[npt.NDArray[np.float64]] = []

        x_cols = file_data.get_loadings_from_adsorbed.pos_x  # type: ignore[attr-defined]
        nt = file[
            :,
            file_data.get_loadings_from_adsorbed.pos_nt,  # type: ignore[attr-defined]
        ]
        for index in range(len(file_data.adsorbates)):
            try:
                component_compositions = file[:, x_cols[index]]
            except IndexError:
                if file_data.get_loadings_from_adsorbed.get_missing_x_from_eq:  # type: ignore[attr-defined]
                    component_compositions = []

                    for index in range(len(pressures)):
                        x_sum = 0
                        for comp in adsorbed_x_list:
                            x_sum += list(comp)[index]
                        component_compositions.append(1 - x_sum)
                else:
                    raise
            adsorbed_x_list.append(np.array(component_compositions))
            loadings_list.append(np.array(component_compositions * nt))

        return np.array(loadings_list)

    def get_loading_list(
        self,
        file: Any,
        file_data: MixIsothermTextFileData,
        pressures: npt.NDArray[np.float64],
    ) -> npt.NDArray[np.float64]:
        if file_data.get_loadings_from_adsorbed is not None:
            return self.get_loadings_from_adsorbed_compositions(
                file, file_data, pressures
            )

        loadings_list = []
        for index in range(len(file_data.adsorbates)):
            loadings_list.append(file[:, file_data.loadings_cols[index]])
        return np.array(loadings_list)

    def check_conversion_factors(
        self,
        pressures: npt.NDArray[np.float64],
        loadings_list: npt.NDArray[np.float64],
        file_data: MixIsothermTextFileData,
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        if file_data.pressure_conversion_factor_to_Pa is not None:
            pressures = pressures * file_data.pressure_conversion_factor_to_Pa

        if file_data.loadings_conversion_factor_to_mol_per_kg is not None:
            for i, component_loadings in enumerate(loadings_list):
                loadings_list[i] = (
                    component_loadings
                    * file_data.loadings_conversion_factor_to_mol_per_kg
                )

        return pressures, loadings_list

    def get_mix_data(
        self, file_data: MixIsothermTextFileData
    ) -> Tuple[
        npt.NDArray[np.float64],
        npt.NDArray[np.float64],
        npt.NDArray[np.float64],
    ]:
        """
        Method to get multi-component isotherm data from a text file.

        Args:
            file_data (MixIsothermTextFileData): An object containing information about the file, its data columns,
            adsorbates, and conversion factors for pressure and loading.

        Returns:
            Tuple[np.array, np.ndarray, np.ndarray]: A tuple containing three lists: pressures,
            loadings, and compositions.
        """
        file_path = self._folder_path / file_data.file_name

        file = np.loadtxt(file_path)
        pressures = file[:, file_data.pressures_col]
        loadings_list = self.get_loading_list(file, file_data, pressures)
        compositions_list = self.get_bulk_composition(
            file, file_data, pressures
        )

        pressures, loadings_list = self.check_conversion_factors(
            pressures, loadings_list, file_data
        )

        loadings = np.array(loadings_list)
        compositions = np.array(compositions_list)

        assert loadings.shape == compositions.shape

        return pressures, loadings, compositions
