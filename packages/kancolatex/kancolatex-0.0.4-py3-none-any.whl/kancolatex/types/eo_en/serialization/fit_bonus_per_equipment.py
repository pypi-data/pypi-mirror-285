from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Optional

from ...const import EquipmentTypes
from ...equipment_id import EquipmentId
from .fit_bonus_data import FitBonusData


class FitBonusPerEquipment(BaseModel):
    equipmentTypes: Optional[list[EquipmentTypes]] = Field(alias="types", default=None)
    equipmentIds: Optional[list[EquipmentId]] = Field(alias="ids", default=None)
    bonuses: list[FitBonusData] = Field(alias="bonuses")
