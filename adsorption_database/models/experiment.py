from enum import Enum
from typing import List, Optional
from attrs import define

from adsorption_database.models.adsorbent import Adsorbent
from adsorption_database.models.isotherms import MixIsotherm, MonoIsotherm


class ExperimentType(Enum):
    GRAVIMETRIC = "Gravimetric"
    VOLUMETRIC = "Volumetric"
    DYNAMIC = "Dynamic"


@define
class Experiment:
    name: str
    adsorbent: Adsorbent
    experiment_type: ExperimentType
    monocomponent_isotherms: List[MonoIsotherm] = []
    mixture_isotherms: List[MixIsotherm] = []
    comments: Optional[str] = None
    paper_url: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[str] = None
    paper_doi: Optional[List[str]] = None
