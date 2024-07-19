from pydantic import BaseModel
from pydantic import Field

from ...ship_id import ShipId
from .enemy_equipment import DeckBuilderEnemyEquipment


class DeckBuilderEnemyShip(BaseModel):
    id: ShipId = Field(alias="id")
    equipment: list[DeckBuilderEnemyEquipment] = Field(alias="items")
