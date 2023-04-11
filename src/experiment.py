from typing import List, Optional
from attrs import define

from data_types import Adsorbent, ExperimentType
from isotherms import MixIsotherm, MonoIsotherm


@define
class Experiment:
    name:str
    temperature:str
    adsorbent:Adsorbent
    experiment_type:ExperimentType
    monocomponent_isotherms: List[MonoIsotherm] = []
    mixture_isotherms: List[MixIsotherm] = []
    comments:Optional[str] = None
    paper_url:Optional[str] = None
    authors:Optional[List[str]]= None
    year:Optional[str] = None
