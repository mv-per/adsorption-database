from typing import List, Optional
from attrs import define
from data_types import Adsorbent, Adsorbate, ExperimentType, IsothermType

@define
class MonoIsotherm:
    name:str
    isotherm_type:IsothermType
    adsorbate:Adsorbate
    pressures:List[float]
    loadings:List[float]
    heats_of_adsorption:List[float] = []
    comments:Optional[str] = None

@define
class MixIsotherm:
    name:str
    isotherm_type:IsothermType
    adsorbates: List[Adsorbate]
    bulk_composition:List[List[float]]
    pressures:List[float]
    loadings:List[List[float]]
    comments:Optional[str] = None