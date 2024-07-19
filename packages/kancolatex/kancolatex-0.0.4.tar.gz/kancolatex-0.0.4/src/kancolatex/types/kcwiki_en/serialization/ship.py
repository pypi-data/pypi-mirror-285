from pydantic import BaseModel
from pydantic import Field

from ...ship_id import ShipId
from .ship_equipment import KcwikiShipEquipment


class KcwikiShip(BaseModel):
    id: ShipId = Field(alias="_api_id")
    losMin: int = Field(alias="_los")
    losMax: int = Field(alias="_los_max")
    equipment: list[KcwikiShipEquipment] = Field(alias="_equipment")

    nameEnglish: str = Field(alias="_name")
    nameJapanese: str = Field(alias="_japanese_name")
    nameFull: str = Field(alias="_full_name")

    # others attribute are not important in this project, implement later.
