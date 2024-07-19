from pydantic import BaseModel
from pydantic import Field


class KcwikiShipEquipment(BaseModel):
    equipment: str | bool = Field(alias="equipment")
    size: int = Field(alias="size")
