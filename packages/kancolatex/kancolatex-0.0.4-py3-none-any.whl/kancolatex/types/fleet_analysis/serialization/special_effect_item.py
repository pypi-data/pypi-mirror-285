from pydantic import BaseModel
from pydantic import Field

from ...const import SpEffectItemKind


class FleetAnalysisSpecialEffectItem(BaseModel):
    apiKind: SpEffectItemKind = Field(alias="api_kind")
    firepower: int = Field(alias="api_houg")
    torpedo: int = Field(alias="api_raig")
    armor: int = Field(alias="api_souk")
    evasion: int = Field(alias="api_kaih")
