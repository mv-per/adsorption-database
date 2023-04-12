from enum import Enum
from typing import Optional

from attr import define

@define
class Adsorbate:
    name:str
    chemical_formula:Optional[str] = None