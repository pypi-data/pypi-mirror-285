from pydantic import BaseModel
from pydantic import Field

from ...equipment_id import EquipmentId


class DeckBuilderEnemyEquipment(BaseModel):
    id: EquipmentId = Field(alias="id")
