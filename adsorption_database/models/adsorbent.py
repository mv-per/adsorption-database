from enum import Enum
from typing import Optional

from attr import define


class AdsorbentType(Enum):
    ZEOLITE = "Zeolite"
    ACTIVATED_CARBON = "Activated Carbon"
    MOF = "Metal-organic framework"
    SILICA = "Silica"


@define
class Adsorbent:
    type: AdsorbentType
    name: str
    void_volume: Optional[float] = None
    density: Optional[float] = None
