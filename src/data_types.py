from enum import Enum
from typing import List, Optional

from attr import define


class AdsorbentType(Enum):
    ZEOLITE='Zeolite'
    ACTIVATED_CARBON='Activated Carbon'
    MOF='Metal-organic framework'
    SILICA='Silica'

class AdsorbateType(Enum):
    GAS='Gas'
    LIQUID='Liquid'
    IONIC_LIQUID='Ionic Liquid'

class ExperimentType(Enum):
    GRAVIMETRIC='Gravimetric'
    VOLUMETRIC='Volumetric'
    DYNAMIC='Dynamic'

class IsothermType(Enum):
    EXCESS='Excess'
    ABSOLUTE='Absolute'


@define
class Adsorbent:
    type:AdsorbentType
    name:str
    density:Optional[float] = None

@define
class Adsorbate:
    type:AdsorbateType
    name:str
    chemical_formula:Optional[str] = None

@define
class MonoIsothermFileData:
    file_name:str
    adsorbate:Adsorbate
    pressures_col:int
    loadings_col:int
    pressure_conversion_factor_to_Pa:Optional[float] = None
    loadings_conversion_factor_to_mol_per_kg:Optional[float] = None

@define
class MixIsothermFileData:
    file_name:str
    adsorbates:List[Adsorbate]
    pressures_col:int
    loadings_cols:List[int]
    composition_cols:List[int]
    load_missing_composition_from_equilibrium:Optional[bool]=False
    pressure_conversion_factor_to_Pa:Optional[float] = None
    loadings_conversion_factor_to_mol_per_kg:Optional[float] = None