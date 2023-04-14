from pathlib import Path
from typing import List, Optional, Tuple

from attr import define
from adsorption_database.models import MonoIsothermFileData, MixIsothermFileData
from adsorption_database.handlers.abstract_handler import AbstractHandler
import numpy as np

import numpy.typing as npt


@define
class MonoIsothermTextFileData(MonoIsothermFileData):
    pressures_col: int
    loadings_col: int
    pressure_conversion_factor_to_Pa: Optional[float] = None
    loadings_conversion_factor_to_mol_per_kg: Optional[float] = None


@define
class MixIsothermTextFileData(MixIsothermFileData):
    pressures_col: int
    loadings_cols: List[int]
    composition_cols: List[int]
    load_missing_composition_from_equilibrium: Optional[bool] = False
    pressure_conversion_factor_to_Pa: Optional[float] = None
    loadings_conversion_factor_to_mol_per_kg: Optional[float] = None


class TextFileHandler(AbstractHandler[MonoIsothermTextFileData, MixIsothermTextFileData]):
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

        if file_data.pressure_conversion_factor_to_Pa is not None:
            pressures = pressures[:] * file_data.pressure_conversion_factor_to_Pa

        if file_data.loadings_conversion_factor_to_mol_per_kg is not None:
            loadings = loadings[:] * file_data.loadings_conversion_factor_to_mol_per_kg

        assert pressures.shape == loadings.shape

        return pressures, loadings

    def get_mix_data(
        self, file_data: MixIsothermTextFileData
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
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

        loadings_list: List[npt.NDArray[np.float64]] = []
        compositions_list: List[npt.NDArray[np.float64]] = []
        for index in range(len(file_data.adsorbates)):
            loadings_list.append(file[:, file_data.loadings_cols[index]])

            try:
                component_compositions = file[:, file_data.composition_cols[index]]
            except IndexError:
                if file_data.load_missing_composition_from_equilibrium:
                    component_compositions = []

                    for index in range(len(pressures)):
                        x_sum = 0
                        for comp in compositions_list:
                            x_sum += list(comp)[index]
                        component_compositions.append(1 - x_sum)
                else:
                    raise
            compositions_list.append(np.array(component_compositions))

        if file_data.pressure_conversion_factor_to_Pa is not None:
            pressures = pressures * file_data.pressure_conversion_factor_to_Pa

        if file_data.loadings_conversion_factor_to_mol_per_kg is not None:

            for i, component_loadings in enumerate(loadings_list):
                loadings_list[i] = (
                    component_loadings * file_data.loadings_conversion_factor_to_mol_per_kg
                )

        loadings = np.array(loadings_list)
        compositions = np.array(compositions_list)

        assert loadings.shape == compositions.shape

        return pressures, loadings, compositions
