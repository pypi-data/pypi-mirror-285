from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Optional

from .equipment import DeckBuilderEquipment


class DeckBuilderAirBaseEquipmentList(BaseModel):
    equipment1: Optional[DeckBuilderEquipment] = Field(alias="i1", default=None)
    equipment2: Optional[DeckBuilderEquipment] = Field(alias="i2", default=None)
    equipment3: Optional[DeckBuilderEquipment] = Field(alias="i3", default=None)
    equipment4: Optional[DeckBuilderEquipment] = Field(alias="i4", default=None)
