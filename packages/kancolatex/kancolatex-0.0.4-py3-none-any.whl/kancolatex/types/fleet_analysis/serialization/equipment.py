from pydantic import BaseModel
from pydantic import Field

from ...equipment_id import EquipmentId


class FleetAnalysisEquipment(BaseModel):
    id: EquipmentId = Field(alias="api_slotitem_id")
    level: int = Field(alias="api_level")
