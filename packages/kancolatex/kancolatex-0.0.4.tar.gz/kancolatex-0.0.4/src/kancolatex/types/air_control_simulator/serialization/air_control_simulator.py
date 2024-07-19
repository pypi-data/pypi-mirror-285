from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Iterable
from typing_extensions import Optional

from ...deck_builder import DeckBuilderData
from ...fleet_analysis import FleetAnalysisEquipment
from ...fleet_analysis import FleetAnalysisShip


class AirControlSimulator(BaseModel):
    fleet: Optional[DeckBuilderData] = Field(alias="predeck")
    ships: Optional[Iterable[FleetAnalysisShip]] = Field(alias="ships")
    equipment: Optional[Iterable[FleetAnalysisEquipment]] = Field(alias="items")
