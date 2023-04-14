from enum import Enum
from typing import List, Optional
from attrs import define
import numpy as np
from adsorption_database.models.adsorbate import Adsorbate
import numpy.typing as npt


@define
class MonoIsothermFileData:
    file_name: str
    adsorbate: Adsorbate


@define
class MixIsothermFileData:
    file_name: str
    adsorbates: List[Adsorbate]


class IsothermType(Enum):
    EXCESS = "Excess"
    ABSOLUTE = "Absolute"


@define
class Isotherm:
    name: str
    isotherm_type: IsothermType
    temperature: float
    comments: Optional[str]


@define
class MonoIsotherm(Isotherm):
    adsorbate: Adsorbate
    pressures: npt.NDArray[np.float64]
    loadings: npt.NDArray[np.float64]
    heats_of_adsorption: Optional[npt.NDArray[np.float64]] = None
    comments: Optional[str] = None


@define
class MixIsotherm(Isotherm):
    adsorbates: List[Adsorbate]
    bulk_composition: npt.NDArray[np.float64]
    pressures: npt.NDArray[np.float64]
    loadings: npt.NDArray[np.float64]
    comments: Optional[str] = None
