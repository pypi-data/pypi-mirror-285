from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Iterable

from ...ship_id import ShipId
from .special_effect_item import FleetAnalysisSpecialEffectItem


class FleetAnalysisShip(BaseModel):
    dropId: int = Field(alias="api_id")
    shipId: ShipId = Field(alias="api_ship_id")
    level: int = Field(alias="api_lv")
    modification: Iterable[int] = Field(alias="api_kyouka")
    experience: Iterable[float] = Field(alias="api_exp")
    expansionSlot: int = Field(alias="api_slot_ex")
    sallyArea: int = Field(alias="api_sally_area")
    specialEffectItems: list[FleetAnalysisSpecialEffectItem] = Field(
        alias="api_sp_effect_items"
    )
