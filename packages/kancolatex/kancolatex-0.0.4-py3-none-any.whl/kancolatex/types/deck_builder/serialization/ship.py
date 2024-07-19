from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from typing_extensions import Optional
from typing_extensions import Sequence

from ...ship_id import ShipId
from .equipment_list import DeckBuilderEquipmentList
from .special_effect_item import DeckBuilderSpecialEffectItem


class DeckBuilderShip(BaseModel):
    id: ShipId = Field(alias="id")
    level: int = Field(alias="lv")
    isExpansionSlotAvailable: bool = Field(alias="exa")
    equipment: DeckBuilderEquipmentList = Field(alias="items")
    hp: int = Field(alias="hp")
    antiSubmarine: int = Field(alias="asw")
    luck: int = Field(alias="luck")

    # """ Following attribute only provide by 74EOen"""
    firepower: Optional[int] = Field(alias="fp", default=None)
    torpedo: Optional[int] = Field(alias="tp", default=None)
    antiAir: Optional[int] = Field(alias="aa", default=None)
    armor: Optional[int] = Field(alias="ar", default=None)
    evasion: Optional[int] = Field(alias="ev", default=None)
    los: Optional[int] = Field(alias="los", default=None)
    speed: Optional[int] = Field(alias="sp", default=None)
    range: Optional[int] = Field(alias="ra", default=None)
    SpecialEffectItem: Optional[Sequence[DeckBuilderSpecialEffectItem]] = Field(
        alias="spi", default=None
    )

    model_config = ConfigDict(populate_by_name=True)
